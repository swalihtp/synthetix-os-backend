import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
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