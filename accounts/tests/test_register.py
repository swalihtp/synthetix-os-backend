import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_register_user(api_client):

    url = reverse("register")

    data = {
        "email": "newuser@test.com",
        "password": "StrongPass123",
        "full_name": "New User"
    }

    response = api_client.post(url, data,format="json")
    
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 201
    assert response.data["full_name"] == "New User"
    assert response.data["email"] == "newuser@test.com"