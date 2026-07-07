import base64
import json

import pytest
from django.urls import reverse
from unittest.mock import patch


@pytest.mark.django_db
def test_gmail_webhook_without_data_returns_ok(api_client):
    response = api_client.post(
        reverse("gmail-pubsub-webhook"),
        {"message": {}},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["message"] == "No data"


@pytest.mark.django_db
@patch("triggers.views.process_gmail_notification_task.delay")
def test_gmail_webhook_dispatches_message(mock_delay, api_client):
    payload = {"historyId": "12345", "emailAddress": "user@example.com"}
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    response = api_client.post(
        reverse("gmail-pubsub-webhook"),
        {
            "message": {
                "data": encoded,
                "messageId": "msg-1",
            }
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["message"] == "Accepted"
    mock_delay.assert_called_once()
