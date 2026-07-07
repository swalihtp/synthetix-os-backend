from rest_framework import serializers
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone_number",
            "profile_image",
            "is_verified",
            "mfa_enabled",
            "role",
            "is_active"
        ]
        read_only_fields = [
            "id",
            "email",
            "is_verified",
            "mfa_enabled",
            "role",
            "is_active"

        ]
