from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PasskeyCredential

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)


class PasskeyCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasskeyCredential
        fields = ('id', 'credential_id', 'created_at')
        read_only_fields = ('id', 'created_at')

