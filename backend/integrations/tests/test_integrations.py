import base64
import json
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from rest_framework import status

from integrations.models import Integration


@pytest.mark.django_db
def test_connection_status_empty(authenticated_client):
    client, user = authenticated_client

    url = reverse("integration-connection-status")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    assert response.data == {
        "gmail": False,
        "google_calendar": False,
        "slack": False,
        "telegram": False,
    }


@pytest.mark.django_db
def test_connection_status_with_integrations(authenticated_client):
    client, user = authenticated_client

    Integration.objects.create(
        user=user,
        provider="gmail",
        access_token="token",
        refresh_token="refresh",
        is_active=True,
    )

    Integration.objects.create(
        user=user,
        provider="slack",
        access_token="token",
        refresh_token="refresh",
        is_active=True,
    )

    url = reverse("integration-connection-status")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK

    assert response.data == {
        "gmail": True,
        "google_calendar": False,
        "slack": True,
        "telegram": False,
    }


@pytest.mark.django_db
def test_gmail_connect_requires_agent_id(authenticated_client):
    client, user = authenticated_client

    url = reverse("gmail-connect")

    response = client.post(url, {})

    assert response.status_code == 400
    assert response.data["error"] == "agent_id is required"


@pytest.mark.django_db
@patch("integrations.views.Flow")
def test_gmail_connect_success(mock_flow, authenticated_client):
    client, user = authenticated_client

    mock_instance = Mock()
    mock_instance.authorization_url.return_value = (
        "https://google.com/auth?code_challenge=test",
        None,
    )

    mock_flow.from_client_config.return_value = mock_instance

    url = reverse("gmail-connect")

    response = client.post(
        url,
        {"agent_id": "123"},
        format="json",
    )

    assert response.status_code == 200

    assert "authorization_url" in response.data


@pytest.mark.django_db
def test_gmail_callback_missing_code(api_client):
    url = reverse("gmail-callback")

    response = api_client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_gmail_callback_missing_state(client):
    url = reverse("gmail-callback")

    response = client.get(
        url,
        {"code": "abc123"},
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_gmail_callback_invalid_state(client):
    url = reverse("gmail-callback")

    response = client.get(
        url,
        {
            "code": "abc123",
            "state": "invalid",
        },
    )

    assert response.status_code == 302


@pytest.mark.django_db
@patch("integrations.views.req.post")
def test_gmail_callback_token_error(
    mock_post,
    client,
    create_user,
):
    user = create_user(email="user@test.com")

    state = base64.urlsafe_b64encode(
        json.dumps(
            {
                "user_id": str(user.id),
                "agent_id": "123",
            }
        ).encode()
    ).decode()

    mock_post.return_value.json.return_value = {"error": "invalid_grant"}

    url = reverse("gmail-callback")

    response = client.get(
        url,
        {
            "code": "abc123",
            "state": state,
        },
    )

    assert response.status_code == 302


@pytest.mark.django_db
@patch("integrations.views.register_gmail_watch")
@patch("integrations.views.req.post")
def test_gmail_callback_success(
    mock_post,
    mock_watch,
    client,
    create_user,
):
    user = create_user(email="user@test.com")

    state = base64.urlsafe_b64encode(
        json.dumps(
            {
                "user_id": str(user.id),
                "agent_id": "123",
            }
        ).encode()
    ).decode()

    mock_post.return_value.json.return_value = {
        "access_token": "access123",
        "refresh_token": "refresh123",
    }

    url = reverse("gmail-callback")

    response = client.get(
        url,
        {
            "code": "abc123",
            "state": state,
        },
    )

    assert response.status_code == 302

    integration = Integration.objects.get(
        user=user,
        provider="gmail",
    )

    assert integration.access_token == "access123"
    assert integration.refresh_token == "refresh123"

    mock_watch.assert_called_once_with(user)


@pytest.mark.django_db
@patch("integrations.views.register_gmail_watch")
def test_gmail_watch_success(
    mock_watch,
    authenticated_client,
):
    client, user = authenticated_client

    mock_watch.return_value = {
        "expiration": "123",
        "historyId": "456",
    }

    url = reverse("gmail-watch")

    response = client.post(url)

    assert response.status_code == 200

    assert response.data["historyId"] == "456"

    mock_watch.assert_called_once_with(user)


@pytest.mark.django_db
@patch("integrations.views.register_gmail_watch")
def test_gmail_watch_failure(
    mock_watch,
    authenticated_client,
):
    client, user = authenticated_client

    mock_watch.side_effect = Exception("watch failed")

    url = reverse("gmail-watch")

    response = client.post(url)

    assert response.status_code == 400

    assert response.data["error"] == "watch failed"


@pytest.mark.django_db
def test_integration_list_and_detail(authenticated_client):
    client, user = authenticated_client

    integration = Integration.objects.create(
        user=user,
        provider="gmail",
        access_token="token",
        refresh_token="refresh",
        is_active=True,
    )

    list_response = client.get(reverse("integration-list"))
    detail_response = client.get(reverse("integration-detail", kwargs={"pk": integration.id}))

    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.data) == 1
    assert list_response.data[0]["provider"] == "gmail"
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["provider"] == "gmail"

