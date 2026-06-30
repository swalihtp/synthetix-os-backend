import pytest
from django.urls import reverse
from accounts.models import Role

@pytest.mark.django_db
def test_get_profile(api_client, create_user):

    

    role = Role.objects.create(name="User")

    user = create_user(role=role)

    api_client.force_authenticate(user=user)

    url = reverse("profile")

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["email"] == user.email