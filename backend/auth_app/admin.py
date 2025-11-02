from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import PasskeyCredential

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(PasskeyCredential)
class PasskeyCredentialAdmin(admin.ModelAdmin):
    list_display = ('user', 'credential_id', 'counter', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'credential_id')

