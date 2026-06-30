import pytest
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode


@pytest.mark.django_db
def test_change_password(api_client, create_user):

    user = create_user()

    api_client.force_authenticate(user=user)

    url = reverse("change-password")

    data = {"old_password": "testpass123", "new_password": "newpass123"}

    response = api_client.post(url, data)

    assert response.status_code == 200
    assert response.data["message"] == "Password updated"


@pytest.mark.django_db
def test_forgot_password(api_client, create_user):

    user = create_user()

    url = reverse("forgot-password")

    response = api_client.post(url, {"email": user.email})

    assert response.status_code == 200
    assert "message" in response.data


@pytest.mark.django_db
def test_reset_password(api_client, create_user):
    user = create_user(password="oldpassword123")

    uid = urlsafe_base64_encode(force_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)

    url = reverse("reset-password")

    response = api_client.post(
        url,
        {
            "uid": uid,
            "token": token,
            "new_password": "newpassword123",
            "confirm_password": "newpassword123",
        },
        format="json",
    )

    user.refresh_from_db()

    assert response.status_code == 200
    assert response.data["message"] == "Password reset successful"
    assert user.check_password("newpassword123")
