import pytest
from django.urls import reverse
from unittest.mock import patch
from workflows.models import DailyAIUsageSnapshot, WorkflowExecution, EmailExecution
from django.conf import settings
import uuid
from django.utils import timezone
from datetime import timedelta
from agent.models import Agent, BuiltInAgent
from workflows.models import Workflow
from accounts.models import Role


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


@pytest.mark.django_db
def test_workflow_execution_stats(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    agent = Agent.objects.create(user=admin_user, name="Admin Agent")
    workflow = Workflow.objects.create(
        agent=agent,
        name="Stats Workflow",
        trigger_type="manual",
        trigger_config={},
    )

    WorkflowExecution.objects.create(workflow=workflow, status="SUCCESS")
    WorkflowExecution.objects.create(workflow=workflow, status="FAILED")
    WorkflowExecution.objects.create(workflow=workflow, status="RUNNING")

    response = api_client.get(reverse("workflow-execution-statitics"))

    assert response.status_code == 200
    assert response.data["summary"]["total"] == 3
    assert response.data["summary"]["success"] == 1
    assert response.data["summary"]["failed"] == 1
    assert response.data["summary"]["running"] == 1
    assert len(response.data["daily"]) == 1


@pytest.mark.django_db
def test_admin_email_activity_stream(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)

    agent = Agent.objects.create(user=admin_user, name="Activity Agent")
    workflow = Workflow.objects.create(
        agent=agent,
        name="Activity Workflow",
        trigger_type="manual",
        trigger_config={},
    )
    workflow_execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status="SUCCESS",
    )
    EmailExecution.objects.create(
        agent=agent,
        workflow_execution=workflow_execution,
        email_id="email-1",
        sender="sender@example.com",
        recipient="admin@example.com",
        original_subject="Subject",
        detected_intent="intent",
        confidence_score=0.95,
        result="AUTO_RESOLVED",
        review_reason="fine",
    )

    response = api_client.get(reverse("admin-email-activity-stream"))

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["activities"][0]["email_id"] == "email-1"


@pytest.mark.django_db
def test_user_registry_user_detail_and_builtin_agents(
    api_client,
    admin_user,
    create_user,
):
    api_client.force_authenticate(user=admin_user)

    role = Role.objects.create(name="viewer")
    target_user = create_user(email="target@test.com", role=role)

    agent = Agent.objects.create(user=target_user, name="Target Agent")
    workflow = Workflow.objects.create(
        agent=agent,
        name="Target Workflow",
        trigger_type="manual",
        trigger_config={},
    )
    WorkflowExecution.objects.create(workflow=workflow, status="SUCCESS")
    WorkflowExecution.objects.create(workflow=workflow, status="FAILED")

    BuiltInAgent.objects.create(
        name="Builtin Admin Agent",
        description="Desc",
        prompt_template="Prompt",
        workflow_configuration={"steps": []},
    )

    registry_response = api_client.get(reverse("user-registry"))
    detail_response = api_client.get(reverse("user-detail", kwargs={"pk": target_user.id}))
    builtin_response = api_client.get(reverse("builtin-agent-list"))

    assert registry_response.status_code == 200
    assert registry_response.data["count"] >= 2
    assert detail_response.status_code == 200
    assert detail_response.data["stats"][0]["value"] == 1
    assert detail_response.data["stats"][1]["value"] == 2
    assert builtin_response.status_code == 200
    assert builtin_response.data["results"][0]["name"] == "Builtin Admin Agent"
