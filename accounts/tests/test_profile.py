import pytest
from django.urls import reverse
from accounts.models import Role, Permission

@pytest.mark.django_db
def test_get_profile(api_client, create_user):

    permission = Permission.objects.create(
        name="View Profile",
        code="view_profile"
    )

    role = Role.objects.create(name="User")
    role.permissions.add(permission)

    user = create_user(role=role)

    api_client.force_authenticate(user=user)

    url = reverse("profile")

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["email"] == user.email