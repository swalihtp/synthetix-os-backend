import pytest
from django.urls import reverse
from accounts.models import EmailVerification
from accounts.utils.otp_geneation import hash_otp, get_expiry
from unittest.mock import patch

@pytest.mark.django_db
def test_verify_email(api_client, create_user):
    user = create_user(is_verified=False)

    EmailVerification.objects.create(
        user=user,
        otp=hash_otp("123456"),
        expires_at=get_expiry(),
    )

    url = reverse("verify-email")

    response = api_client.post(
        url,
        {
            "email": user.email,
            "otp": "123456",
        },
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert response.data["message"] == "Email verified successfully"
    assert user.is_verified is True
    assert not EmailVerification.objects.filter(user=user).exists()





@pytest.mark.django_db
@patch("accounts.views.EmailService.send_verification_email")
def test_resend_verification_otp(
    mock_send_email,
    api_client,
    create_user,
):
    user = create_user(is_verified=False)

    url = reverse("resend-verification")

    response = api_client.post(
        url,
        {"email": user.email},
        format="json",
    )
    print(response.status_code)
    print(response.data)

    assert response.status_code == 200
    assert response.data["message"] == "Verification code sent"

    mock_send_email.assert_called_once()

    assert EmailVerification.objects.filter(user=user).exists()
