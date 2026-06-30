import pytest
from rest_framework import status
from agent.models import Agent
from django.urls import reverse


@pytest.mark.django_db
def test_list_agents_returns_only_current_user_agents(api_client, create_user):
    user1 = create_user(email="user1@test.com")
    user2 = create_user(email="user2@test.com")

    Agent.objects.create(user=user1, name="Agent 1", description="User1 Agent")

    Agent.objects.create(user=user2, name="Agent 2", description="User2 Agent")

    api_client.force_authenticate(user=user1)

    url = reverse("agent-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Agent 1"


@pytest.mark.django_db
def test_create_agent(api_client, create_user):
    user = create_user(email="user@test.com")

    api_client.force_authenticate(user=user)

    payload = {
        "name": "Resume Analyzer",
        "description": "Analyze resumes",
        "prompt": "Review this resume",
    }

    url = reverse("agent-list")

    response = api_client.post(url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    agent = Agent.objects.get(name="Resume Analyzer")

    assert agent.user == user
    assert agent.description == payload["description"]
    assert agent.prompt == payload["prompt"]


@pytest.mark.django_db
def test_list_agents_requires_authentication(api_client):
    url = reverse("agent-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_other_user_agent_returns_404(api_client, create_user):
    user1 = create_user(email="user1@test.com")
    user2 = create_user(email="user2@test.com")

    agent = Agent.objects.create(user=user2, name="Private Agent")

    api_client.force_authenticate(user=user1)

    url = reverse("agent-detail", kwargs={"pk": agent.id})

    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_own_agent(api_client, create_user):
    user = create_user(email="user@test.com")

    agent = Agent.objects.create(
        user=user, name="My Agent", description="My Description"
    )

    url = reverse("agent-detail", kwargs={"pk": agent.id})

    api_client.force_authenticate(user=user)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "My Agent"


@pytest.mark.django_db
def test_update_agent(api_client, create_user):
    user = create_user(email="user@test.com")

    agent = Agent.objects.create(user=user, name="Old Name")

    api_client.force_authenticate(user=user)

    url = reverse("agent-detail", kwargs={"pk": agent.id})

    response = api_client.patch(
        url,
        {"name": "New Name"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    agent.refresh_from_db()

    assert agent.name == "New Name"


@pytest.mark.django_db
def test_delete_agent(api_client, create_user):
    user = create_user(email="user@test.com")

    agent = Agent.objects.create(user=user, name="Agent To Delete")

    api_client.force_authenticate(user=user)

    url = reverse("agent-detail", kwargs={"pk": agent.id})

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Agent.objects.filter(id=agent.id).exists()
