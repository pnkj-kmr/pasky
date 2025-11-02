// WebAuthn utility functions

/**
 * Convert base64url string to Uint8Array
 */
export function base64UrlToUint8Array(base64url: string): Uint8Array {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

/**
 * Convert Uint8Array to base64url string
 */
export function uint8ArrayToBase64Url(bytes: Uint8Array): string {
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  const base64 = btoa(binary);
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

/**
 * Check if WebAuthn is supported
 */
export function isWebAuthnSupported(): boolean {
  return typeof window !== 'undefined' &&
    typeof window.PublicKeyCredential !== 'undefined';
}

/**
 * Create credential for registration
 */
export async function createCredential(
  options: any
): Promise<PublicKeyCredential> {
  if (!isWebAuthnSupported()) {
    throw new Error('WebAuthn is not supported in this browser');
  }

  // Convert challenge from base64url to ArrayBuffer
  const challenge = base64UrlToUint8Array(options.challenge);

  // Convert user ID from base64url to ArrayBuffer
  const userId = base64UrlToUint8Array(options.user.id);

  // Create public key credential creation options
  const publicKeyCredentialCreationOptions: PublicKeyCredentialCreationOptions = {
    challenge,
    rp: options.rp,
    user: {
      ...options.user,
      id: userId,
    },
    pubKeyCredParams: options.pubKeyCredParams,
    authenticatorSelection: options.authenticatorSelection,
    timeout: options.timeout,
    attestation: options.attestation as AttestationConveyancePreference,
  };

  try {
    const credential = await navigator.credentials.create({
      publicKey: publicKeyCredentialCreationOptions,
    }) as PublicKeyCredential | null;

    if (!credential) {
      throw new Error('Failed to create credential');
    }

    return credential;
  } catch (error: any) {
    throw new Error(`Credential creation failed: ${error.message}`);
  }
}

/**
 * Get credential for authentication
 */
export async function getCredential(
  options: any
): Promise<PublicKeyCredential> {
  if (!isWebAuthnSupported()) {
    throw new Error('WebAuthn is not supported in this browser');
  }

  // Convert challenge from base64url to ArrayBuffer
  const challenge = base64UrlToUint8Array(options.challenge);

  // Convert allowCredentials IDs
  const allowCredentials = options.allowCredentials.map((cred: any) => ({
    ...cred,
    id: base64UrlToUint8Array(cred.id),
  }));

  // Create public key credential request options
  const publicKeyCredentialRequestOptions: PublicKeyCredentialRequestOptions = {
    challenge,
    allowCredentials,
    timeout: options.timeout,
    userVerification: options.userVerification as UserVerificationRequirement,
    rpId: options.rpId,
  };

  try {
    const credential = await navigator.credentials.get({
      publicKey: publicKeyCredentialRequestOptions,
    }) as PublicKeyCredential | null;

    if (!credential) {
      throw new Error('Failed to get credential');
    }

    return credential;
  } catch (error: any) {
    throw new Error(`Credential retrieval failed: ${error.message}`);
  }
}

/**
 * Convert PublicKeyCredential to JSON for API
 */
export function credentialToJSON(credential: PublicKeyCredential): any {
  const response = credential.response as AuthenticatorAttestationResponse | AuthenticatorAssertionResponse;

  if ('attestationObject' in response) {
    // Registration response
    const attestationResponse = response as AuthenticatorAttestationResponse;
    return {
      id: credential.id,
      rawId: uint8ArrayToBase64Url(new Uint8Array(credential.rawId)),
      response: {
        clientDataJSON: uint8ArrayToBase64Url(
          new Uint8Array(attestationResponse.clientDataJSON)
        ),
        attestationObject: uint8ArrayToBase64Url(
          new Uint8Array(attestationResponse.attestationObject)
        ),
      },
      type: credential.type,
    };
  } else {
    // Authentication response
    const assertionResponse = response as AuthenticatorAssertionResponse;
    return {
      id: credential.id,
      rawId: uint8ArrayToBase64Url(new Uint8Array(credential.rawId)),
      response: {
        clientDataJSON: uint8ArrayToBase64Url(
          new Uint8Array(assertionResponse.clientDataJSON)
        ),
        authenticatorData: uint8ArrayToBase64Url(
          new Uint8Array(assertionResponse.authenticatorData)
        ),
        signature: uint8ArrayToBase64Url(
          new Uint8Array(assertionResponse.signature)
        ),
        userHandle: assertionResponse.userHandle
          ? uint8ArrayToBase64Url(new Uint8Array(assertionResponse.userHandle))
          : null,
      },
      type: credential.type,
    };
  }
}

