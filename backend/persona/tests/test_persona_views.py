import pytest
from django.urls import reverse

from persona.models import UserPersona


def _full_persona_payload():
    return {
        "display_name": "Alex",
        "role": "developer",
        "industry": "Software",
        "experience_years": 5,
        "primary_goals": "Ship quality software",
        "business_description": "Builds products",
        "ai_tone": "professional",
        "response_style": "detailed",
        "ai_priority": "balanced",
        "ai_avoidances": "Avoid fluff",
        "communication_style": "Direct",
        "common_messages": "Thanks for the update",
        "manages_projects": True,
        "workday_improvements": "Automate follow-ups",
        "important_documents": "Specs",
        "brand_guidelines": "Keep it simple",
        "long_term_memory": "Prefers concise summaries",
        "privacy_preferences": "Do not share data",
    }


@pytest.mark.django_db
def test_persona_create_update_completion_and_destroy(authenticated_client):
    client, user = authenticated_client

    response = client.post(
        reverse("persona-list"),
        _full_persona_payload(),
        format="json",
    )

    assert response.status_code == 200
    persona = UserPersona.objects.get(user=user)
    assert persona.completed is True
    assert persona.completion_percentage == 100

    update_response = client.patch(
        reverse("persona-detail", kwargs={"pk": persona.id}),
        {"display_name": "Alex Updated"},
        format="json",
    )

    persona.refresh_from_db()

    assert update_response.status_code == 200
    assert persona.display_name == "Alex Updated"

    completion_response = client.get(reverse("persona-completion"))
    metadata_response = client.get(reverse("persona-metadata"))

    assert completion_response.status_code == 200
    assert completion_response.data["completed"] is True
    assert metadata_response.status_code == 200
    assert any(choice["value"] == "developer" for choice in metadata_response.data["role_choices"])

    delete_response = client.delete(reverse("persona-detail", kwargs={"pk": persona.id}))

    assert delete_response.status_code == 200
    assert not UserPersona.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_persona_list_returns_current_persona(authenticated_client):
    client, user = authenticated_client

    persona = UserPersona.objects.create(
        user=user,
        display_name="Existing Persona",
        role="other",
    )

    response = client.get(reverse("persona-list"))

    assert response.status_code == 200
    assert response.data["display_name"] == "Existing Persona"
