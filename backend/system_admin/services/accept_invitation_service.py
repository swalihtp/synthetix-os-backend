from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from system_admin.models import AdminInvitation

@transaction.atomic
def accept_invitation(token, password):
    invitation = get_object_or_404(AdminInvitation, token=token, is_used=False)

    if invitation.expires_at < timezone.now():
        raise ValidationError("Invitation expired")

    user = invitation.user

    user.set_password(password)
    user.is_verified = True
    user.save()

    invitation.is_used = True
    invitation.save()
