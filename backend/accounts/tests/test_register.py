import pytest
from django.urls import reverse
from accounts.models import Role


@pytest.mark.django_db
def test_register_user(api_client):
    Role.objects.create(name="user")
    url = reverse("register")

    data = {
        "email": "newuser@test.com",
        "password": "StrongPass123",
        "full_name": "New User",
        "is_verified": True,
        "is_active": True
    }

    response = api_client.post(url, data,format="json")
    
    print("STATUS:", response.status_code)
    print("DATA:", response.data)
    
    print(f"RESPONSE::{response}")

    assert response.status_code == 201
    assert response.data['message'] == "Registration successful. Please check your email for the verification code. If you not found also check your spam"