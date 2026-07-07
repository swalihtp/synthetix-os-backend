import pytest
from unittest.mock import patch


@pytest.mark.django_db
@patch("dashboard.views.DashboardService.get_dashboard")
def test_dashboard_returns_serialized_payload(mock_get_dashboard, authenticated_client):
    client, user = authenticated_client

    mock_get_dashboard.return_value = {
        "overview": {
            "agents": 2,
            "built_in_agents": 3,
            "workflows": 4,
            "running_workflows": 1,
            "completed_today": 5,
            "failed_today": 0,
        },
        "today_activity": {
            "ai_calls": 8,
            "email_processed": 6,
            "resumes_analyzed": 1,
            "meetings_summarized": 2,
        },
        "continue_working": [],
        "recent_activity": [],
        "applications": [],
        "workflow_statistics": {
            "completed": 4,
            "running": 1,
            "failed": 0,
        },
    }

    response = client.get("/api/dashboard/")

    assert response.status_code == 200
    assert response.data["overview"]["agents"] == 2
    assert response.data["workflow_statistics"]["completed"] == 4


@pytest.mark.django_db
@patch("dashboard.views.DashboardService.get_dashboard", side_effect=Exception("boom"))
def test_dashboard_handles_service_errors(mock_get_dashboard, authenticated_client):
    client, user = authenticated_client

    response = client.get("/api/dashboard/")

    assert response.status_code == 500
    assert response.data["detail"] == "Unable to load dashboard."
