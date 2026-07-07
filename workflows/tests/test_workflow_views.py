import pytest
from agent.models import Agent
from workflows.models import Workflow
from django.urls import reverse


@pytest.mark.django_db
def test_workflow_list_returns_only_user_workflows(
    authenticated_client,
    user,
    other_user,
):
    agent1 = Agent.objects.create(
        user=user,
        name="Agent 1",
    )

    agent2 = Agent.objects.create(
        user=other_user,
        name="Agent 2",
    )

    workflow1 = Workflow.objects.create(
        agent=agent1,
        name="Workflow 1",
        trigger_type="manual",
        trigger_config={},
    )

    Workflow.objects.create(
        agent=agent2,
        name="Workflow 2",
        trigger_type="manual",
        trigger_config={},
    )

    response = authenticated_client.get(reverse("workflow-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == str(workflow1.id)


@pytest.mark.django_db
def test_create_workflow(
    authenticated_client,
    user,
):
    agent = Agent.objects.create(
        user=user,
        name="Agent",
    )

    payload = {
        "agent": str(agent.id),
        "name": "New Workflow",
        "trigger_type": "manual",
        "trigger_config": {},
    }

    response = authenticated_client.post(
        reverse("workflow-list"),
        payload,
        format="json",
    )

    assert response.status_code == 201

    assert Workflow.objects.filter(name="New Workflow").exists()

