import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
def test_logout(api_client, create_user):

    user = create_user()

    refresh = RefreshToken.for_user(user)

    api_client.force_authenticate(user=user)

    url = reverse("logout")

    response = api_client.post(url, {
        "refresh": str(refresh)
    })

    assert response.status_code == 200
    assert response.data["message"] == "Logged out"