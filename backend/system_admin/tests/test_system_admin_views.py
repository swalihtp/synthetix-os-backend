import pytest
from django.urls import reverse
from unittest.mock import patch
from workflows.models import DailyAIUsageSnapshot
from django.conf import settings
import uuid


@pytest.mark.django_db
@patch("system_admin.views.DashboardStatisticsService.get_statistics")
def test_dashboard_statistics_success(mock_get_statistics, api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    mock_get_statistics.return_value = {
        "users": {
            "total": 10,
            "active": 8,
        },
        "agents": {
            "total": 5,
        },
        "workflow_executions": {
            "total": 20,
            "success": 15,
            "failed": 3,
            "running": 2,
        },
    }

    response = api_client.get(reverse("dashboard-statistics"))

    assert response.status_code == 200
    assert response.data["users"]["total"] == 10


@pytest.mark.django_db
def test_generate_ai_usage_snapshot(api_client):
    response = api_client.post(
        reverse("generate-ai-usage-snapshot"),
        HTTP_X_API_KEY=settings.LAMBDA_API_KEY,
    )

    assert response.status_code == 200

    assert DailyAIUsageSnapshot.objects.count() == 1

    assert response.data["message"] == "AI usage snapshot generated"


@pytest.mark.django_db
def test_generate_ai_usage_snapshot_invalid_key(api_client):
    response = api_client.post(
        reverse("generate-ai-usage-snapshot"),
        HTTP_X_API_KEY="invalid",
    )
    print(response.status_code)
    print(response.data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_ai_usage_dashboard_empty(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get(reverse("ai-usage-statitics"))
    
    print(response.status_code)
    print(response.data)

    assert response.status_code == 200

    assert response.data["today"]["total_calls"] == 0
    assert response.data["last_7_days_trend"] == []


@pytest.mark.django_db
def test_block_user(admin_client, create_user):
    user = create_user(email="user@test.com")

    response = admin_client.patch(reverse("block-user", kwargs={"pk": user.id}))

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.is_active is False


@pytest.mark.django_db
def test_block_self(admin_client, admin_user):
    response = admin_client.patch(reverse("block-user", kwargs={"pk": admin_user.id}))

    assert response.status_code == 400
    assert response.data["detail"] == "You cannot block yourself."


@pytest.mark.django_db
def test_activate_user(admin_client, create_user):
    user = create_user(
        email="inactive@test.com",
        is_active=False,
    )

    response = admin_client.patch(reverse("activate-user", kwargs={"pk": user.id}))

    user.refresh_from_db()

    assert response.status_code == 200
    assert user.is_active is True


@pytest.mark.django_db
def test_delete_user(admin_client, create_user):
    user = create_user(email="delete@test.com")

    response = admin_client.delete(reverse("delete-user", kwargs={"pk": user.id}))

    assert response.status_code == 204


@pytest.mark.django_db
def test_delete_self(admin_client, admin_user):
    response = admin_client.delete(reverse("delete-user", kwargs={"pk": admin_user.id}))

    assert response.status_code == 400


@pytest.mark.django_db
@patch("system_admin.views.AdminService.create_admin")
def test_create_admin(mock_create_admin, admin_client):

    payload = {"email": "newadmin@test.com"}

    response = admin_client.post(
        reverse("create-admin"),
        payload,
        format="json",
    )

    assert response.status_code == 201

    mock_create_admin.assert_called_once_with(email="newadmin@test.com")


@pytest.mark.django_db
@patch("system_admin.views.AdminService.accept_invitation")
def test_accept_invitation(
    mock_accept_invitation,
    api_client,
):
    payload = {
        "token": str(uuid.uuid4()),
        "password": "Password123",
    }

    response = api_client.post(
        reverse("accept-invite"),
        payload,
        format="json",
    )

    assert response.status_code == 200

    mock_accept_invitation.assert_called_once()
