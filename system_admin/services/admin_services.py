from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from accounts.models import User,Role
from accounts.services.email_service import EmailService
from system_admin.models import AdminInvitation


class AdminService:

    @staticmethod
    @transaction.atomic
    def create_admin(email):

        if User.objects.filter(email=email).exists():
            raise ValidationError({"email": "User already exists."})

        role = Role.objects.get(name="system_admin")

        user = User.objects.create(
            email=email,
            role=role,
            is_verified=True,
            is_active=True,
        )

        invitation = AdminInvitation.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(days=2),
        )

        invitation_url = (
            f"{settings.FRONTEND_URL}" f"/accept-invite?token={invitation.token}"
        )
        
        EmailService.send_admin_invitation(
            email=email,
            invitation_url=invitation_url,
        )

        return user

    @staticmethod
    @transaction.atomic
    def accept_invitation(token, password):

        try:
            invitation = AdminInvitation.objects.select_related("user").get(
                token=token,
                is_used=False,
            )

        except AdminInvitation.DoesNotExist:
            raise ValidationError({"token": "Invalid invitation."})

        if invitation.expires_at < timezone.now():
            raise ValidationError({"token": "Invitation expired."})

        user = invitation.user

        user.set_password(password)
        user.is_verified = True
        user.save(
            update_fields=[
                "password",
                "is_verified",
            ]
        )

        invitation.is_used = True
        invitation.save(update_fields=["is_used"])

        return user
