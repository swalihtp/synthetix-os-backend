from accounts.models import User, EmailVerification, Role
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from .email_service import EmailService
from django.db import transaction
from accounts.utils.otp_geneation import generate_otp, hash_otp, get_expiry


class AuthService:

    @staticmethod
    @transaction.atomic
    def register_user(data):

        role = Role.objects.get(name="user")
        user = User.objects.create_user(**data, role=role, is_verified=False)
        

        otp = generate_otp()

        EmailVerification.objects.update_or_create(
            user=user, defaults={"otp": hash_otp(otp), "expires_at": get_expiry()}
        )

        EmailService.send_verification_email(user=user, otp=otp)

        return user

    @staticmethod
    def login_user(user):
        if not user.is_verified:
            raise ValidationError("Email not verified")

        refresh = RefreshToken.for_user(user)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}
