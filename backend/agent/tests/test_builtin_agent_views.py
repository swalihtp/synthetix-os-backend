import pytest
from django.urls import reverse
from rest_framework import status

from agent.models import Agent, BuiltInAgent


@pytest.mark.django_db
def test_builtin_agent_list_and_detail(api_client, create_user):
    user = create_user(email="user@test.com")
    api_client.force_authenticate(user=user)

    agent = BuiltInAgent.objects.create(
        name="Builtin Agent",
        description="Builtin description",
        prompt_template="Prompt template",
        workflow_configuration={"steps": []},
    )

    list_response = api_client.get(reverse("builtin-agent-list"))
    detail_response = api_client.get(reverse("builtin-agent-detail", kwargs={"pk": agent.id}))

    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.data["results"][0]["name"] == "Builtin Agent"
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["name"] == "Builtin Agent"


@pytest.mark.django_db
def test_email_agent_dashboard(api_client, create_user):
    user = create_user(email="user@test.com")
    api_client.force_authenticate(user=user)

    agent = Agent.objects.create(user=user, name="Email Agent")

    response = api_client.get(reverse("email-agent-dashboard", kwargs={"agent_id": agent.id}))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["stats"]["processed_emails"] == 0
    assert response.data["stats"]["auto_resolved_percentage"] == 0
