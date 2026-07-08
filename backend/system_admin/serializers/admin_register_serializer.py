from rest_framework import serializers


class CreateAdminSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(
        min_length=8,
        write_only=True,
    )