import pytest
from rest_framework.test import APIClient


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
            is_verified=kwargs.get("is_verified", True),
            mfa_enabled=kwargs.get("mfa_enabled", False),
            mfa_secret=kwargs.get("mfa_secret", None),
            role=kwargs.get("role", None),
        )

    return make_user


@pytest.fixture
def user(create_user):
    return create_user(email="user@test.com")


@pytest.fixture
def other_user(create_user):
    return create_user(email="other@test.com")


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client, user
