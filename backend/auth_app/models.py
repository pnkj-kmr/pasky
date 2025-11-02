from django.db import models
from django.contrib.auth.models import AbstractUser
import base64
import json


class User(AbstractUser):
    """Extended User model for passkey authentication."""

    email = models.EmailField(unique=True, blank=False, null=False)

    def __str__(self):
        return self.username


class PasskeyCredential(models.Model):
    """Store WebAuthn passkey credentials."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="passkeys")
    credential_id = models.TextField(unique=True)  # Base64 encoded credential ID
    public_key = models.TextField()  # Base64 encoded public key
    counter = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "passkey_credentials"

    def __str__(self):
        return f"{self.user.username} - {self.credential_id[:20]}..."
