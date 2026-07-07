import pytest
from rest_framework.test import APIClient
from accounts.models import Role


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    def make_user(**kwargs):
        return User.objects.create_user(
            email=kwargs.get("email", "test@example.com"),
            password=kwargs.get("password", "testpass123"),
            full_name=kwargs.get("full_name", "Test User"),
            is_verified=True,
            mfa_enabled=kwargs.get("mfa_enabled", False),
            mfa_secret=kwargs.get("mfa_secret", None),
            role=kwargs.get("role", None),
        )

    return make_user


@pytest.fixture
def admin_role(db):
    return Role.objects.create(name="system_admin")


@pytest.fixture
def admin_user(create_user, admin_role):
    return create_user(
        email="admin@test.com",
        role=admin_role,
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
