from accounts.models import User,Role
from system_admin.models import AdminInvitation
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from accounts.services.email_service import EmailService

@transaction.atomic
def create_admin(email):
    role = Role.objects.get(name="system_admin")

    user = User.objects.create(
        email=email,
        role=role,
        is_active=True,
        is_verified=False,
    )

    invitation = AdminInvitation.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(days=2)
    )

    invitation_url = (
        f"{settings.FRONTEND_URL}"
        f"/accept-invite?token={invitation.token}"
    )
    print(f"user info when creatin{user.email}")
    print(f"{type(user.email)}")

    EmailService.send_admin_invitation(
        email=user.email,
        invitation_url=invitation_url
    )

    return user