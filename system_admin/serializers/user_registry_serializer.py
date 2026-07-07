from rest_framework import serializers
from accounts.models import User

class UserRegistrySerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', default=None)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role_name', 'is_verified', 'mfa_enabled', 'created_at','last_login','is_active']