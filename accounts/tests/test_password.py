import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_change_password(api_client, create_user):

    user = create_user()

    api_client.force_authenticate(user=user)

    url = reverse("change-password")

    data = {
        "old_password": "testpass123",
        "new_password": "newpass123"
    }

    response = api_client.post(url, data)

    assert response.status_code == 200
    assert response.data["message"] == "Password updated"
    
    
@pytest.mark.django_db
def test_forgot_password(api_client, create_user):

    user = create_user()

    url = reverse("forgot-password")

    response = api_client.post(url, {
        "email": user.email
    })

    assert response.status_code == 200
    assert "message" in response.data