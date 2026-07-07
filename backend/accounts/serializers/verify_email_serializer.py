from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from accounts.models import User


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):

        email = attrs["email"]
        otp = attrs["otp"]

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email")

        verification = user.email_verification

        if verification.is_expired:
            raise serializers.ValidationError("OTP expired")

        if not check_password(otp, verification.otp):
            raise serializers.ValidationError("Invalid OTP")

        attrs["user"] = user
        return attrs
