from unittest.mock import patch
import pytest
from django.urls import reverse


@pytest.mark.django_db
@patch("accounts.services.google_auth_service.GoogleAuthService.verify_google_token")
def test_google_login(mock_verify, api_client):

    mock_verify.return_value = {
        "email": "google@test.com",
        "name": "Google User"
    }

    url = reverse("google-login")

    response = api_client.post(url, {
        "token": "fake-google-token"
    })

    assert response.status_code == 200
    assert "access" in response.data