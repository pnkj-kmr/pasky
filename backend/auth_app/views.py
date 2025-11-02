from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, login
from django.conf import settings
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers import (
    bytes_to_base64url,
    base64url_to_bytes,
    parse_registration_credential_json,
    parse_authentication_credential_json,
)
from webauthn.helpers.structs import (
    UserVerificationRequirement,
)
import secrets

from .models import PasskeyCredential

User = get_user_model()

# In-memory storage for challenges (use Redis or database in production)
challenge_store = {}


@api_view(["POST"])
@permission_classes([AllowAny])
def register_start(request):
    """Start passkey registration process."""
    username = request.data.get("username")
    email = request.data.get("email")

    if not username or not email:
        return Response(
            {"error": "Username and email are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
        )

    # Create user (but don't save yet - will save after passkey verification)
    user_id = secrets.token_bytes(16)

    # Generate registration options
    options = generate_registration_options(
        rp_id=settings.RP_ID,
        rp_name=settings.RP_NAME,
        user_id=user_id,
        user_name=username,
        user_display_name=username,
    )

    # Store challenge and user data
    challenge = options.challenge
    challenge_store[challenge] = {
        "username": username,
        "email": email,
        "user_id": user_id,
    }

    # Convert options to dict for JSON response
    options_dict = {
        "challenge": bytes_to_base64url(options.challenge),
        "rp": {
            "id": options.rp.id,
            "name": options.rp.name,
        },
        "user": {
            "id": bytes_to_base64url(options.user.id),
            "name": options.user.name,
            "displayName": options.user.display_name,
        },
        "pubKeyCredParams": [
            {"alg": alg.alg.value, "type": alg.type}
            for alg in options.pub_key_cred_params
        ],
        "authenticatorSelection": {
            "authenticatorAttachment": options.authenticator_selection.authenticator_attachment.value
            if options.authenticator_selection
            and options.authenticator_selection.authenticator_attachment
            else None,
            "userVerification": options.authenticator_selection.user_verification.value
            if options.authenticator_selection
            else UserVerificationRequirement.PREFERRED.value,
            "requireResidentKey": options.authenticator_selection.require_resident_key
            if options.authenticator_selection
            else False,
        },
        "timeout": options.timeout,
        "attestation": options.attestation.value,
    }

    return Response(options_dict)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_complete(request):
    """Complete passkey registration process."""
    credential_json = request.data.get("credential")
    challenge_b64 = request.data.get("challenge")

    if not credential_json or not challenge_b64:
        return Response(
            {"error": "Credential and challenge are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Retrieve stored challenge data
    try:
        challenge = base64url_to_bytes(challenge_b64)
        stored_data = challenge_store.pop(challenge, None)

        if not stored_data:
            return Response(
                {"error": "Invalid or expired challenge"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception:
        return Response(
            {"error": "Invalid challenge format"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Parse credential using the new webauthn 2.x API
        credential = parse_registration_credential_json(credential_json)

        # Verify registration
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=settings.RP_ID,
            expected_origin="http://localhost:3000",
        )

        # Create user
        user = User.objects.create_user(
            username=stored_data["username"],
            email=stored_data["email"],
        )

        # Store passkey credential
        PasskeyCredential.objects.create(
            user=user,
            credential_id=bytes_to_base64url(verification.credential_id),
            public_key=bytes_to_base64url(verification.credential_public_key),
            counter=verification.sign_count,
        )

        # Log user in
        login(request, user)

        return Response(
            {
                "message": "Registration successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )

    except Exception as e:
        return Response(
            {"error": f"Verification failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_start(request):
    """Start passkey authentication process."""
    username = request.data.get("username")

    if not username:
        return Response(
            {"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get user's passkeys
    passkeys = PasskeyCredential.objects.filter(user=user)
    if not passkeys.exists():
        return Response(
            {"error": "No passkeys registered for this user"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Prepare allowed credentials
    allowed_credentials = [
        {
            "id": passkey.credential_id,
            "type": "public-key",
        }
        for passkey in passkeys
    ]

    # Generate authentication options
    options = generate_authentication_options(
        rp_id=settings.RP_ID,
        allow_credentials=[
            {
                "id": base64url_to_bytes(passkey.credential_id),
                "type": "public-key",
            }
            for passkey in passkeys
        ],
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    # Store challenge with user ID
    challenge = options.challenge
    challenge_store[challenge] = {
        "user_id": user.id,
        "username": user.username,
    }

    options_dict = {
        "challenge": bytes_to_base64url(options.challenge),
        "allowCredentials": allowed_credentials,
        "timeout": options.timeout,
        "userVerification": options.user_verification.value,
        "rpId": options.rp_id,
    }

    return Response(options_dict)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_complete(request):
    """Complete passkey authentication process."""
    credential_json = request.data.get("credential")
    challenge_b64 = request.data.get("challenge")

    if not credential_json or not challenge_b64:
        return Response(
            {"error": "Credential and challenge are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        challenge = base64url_to_bytes(challenge_b64)
        stored_data = challenge_store.pop(challenge, None)

        if not stored_data:
            return Response(
                {"error": "Invalid or expired challenge"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(id=stored_data["user_id"])

        # Get credential ID from request (prefer rawId, fallback to id)
        credential_id = credential_json.get("rawId") or credential_json.get("id")
        if not credential_id:
            return Response(
                {"error": "Credential ID not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            passkey = PasskeyCredential.objects.get(
                user=user, credential_id=credential_id
            )
        except PasskeyCredential.DoesNotExist:
            # Try the other field if first lookup failed
            alternative_id = (
                credential_json.get("id")
                if credential_id == credential_json.get("rawId")
                else credential_json.get("rawId")
            )
            if alternative_id and alternative_id != credential_id:
                try:
                    passkey = PasskeyCredential.objects.get(
                        user=user, credential_id=alternative_id
                    )
                    credential_id = alternative_id
                except PasskeyCredential.DoesNotExist:
                    return Response(
                        {"error": "Credential not found for this user"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    {"error": "Credential not found for this user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Parse credential using the new webauthn 2.x API
        credential = parse_authentication_credential_json(credential_json)

        # Verify authentication
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=settings.RP_ID,
            expected_origin="http://localhost:3000",
            credential_public_key=base64url_to_bytes(passkey.public_key),
            credential_current_sign_count=passkey.counter,
        )

        # Update counter
        passkey.counter = verification.new_sign_count
        passkey.save()

        # Log user in
        login(request, user)

        return Response(
            {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        )

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(
            {"error": f"Verification failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Get current authenticated user info."""
    return Response(
        {
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token(request):
    """Get CSRF token for the frontend."""
    from django.middleware.csrf import get_token

    token = get_token(request)
    return Response({"csrfToken": token})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout current user."""
    from django.contrib.auth import logout

    logout(request)
    return Response({"message": "Logged out successfully"})
