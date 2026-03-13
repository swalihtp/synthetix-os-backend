import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_login_without_mfa(api_client, create_user):

    user = create_user()

    url = reverse("login")

    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }

    response = api_client.post(url, data,format="json")
    
    print("STATUS:", response.status_code)
    print("DATA:", response.data)

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
    
    
# @pytest.mark.django_db
# def test_login_without_mfa(api_client, create_user):
#     user = create_user()
#     url = reverse("login")
#     data = {
#         "email": "test@example.com",
#         "password": "testpass123"
#     }
#     response = api_client.post(url, data, format="json")
#     print("USER CREATED:", user.email, user.is_verified)
#     print("STATUS:", response.status_code)
#     print("DATA:", response.data)
#     assert response.status_code == 200
        