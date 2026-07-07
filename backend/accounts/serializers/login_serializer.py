from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User=get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not user.check_password(data["password"]):
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data