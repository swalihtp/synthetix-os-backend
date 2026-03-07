from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError

class AuthService:

    @staticmethod
    def register_user(data):
        return User.objects.create_user(**data)

    @staticmethod
    def login_user(user):
        if not user.is_verified:
            raise ValidationError("Email not verified")
        
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        
        