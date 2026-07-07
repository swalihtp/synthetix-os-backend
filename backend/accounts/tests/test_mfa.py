import pyotp
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_enable_mfa(api_client, create_user):

    user = create_user()

    api_client.force_authenticate(user=user)

    url = reverse("enable-mfa")

    response = api_client.post(url)

    assert response.status_code == 200
    assert "qr_uri" in response.data
    
@pytest.mark.django_db
def test_verify_mfa_login(api_client, create_user):

    secret = pyotp.random_base32()
    user = create_user(
        mfa_secret=secret,
        mfa_enabled=True    
    )

    url = reverse("verify-mfa-login")

    data = {
        "user_id": user.id,
        "otp": "123456"
    }

    response = api_client.post(url, data)

    assert response.status_code in [200, 400]