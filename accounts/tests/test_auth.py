import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(email="test@example.com", password="Test@123"):
        user = User.objects.create_user(email=email, username="testuser", password=password)
        return user
    return _create_user



@pytest.mark.django_db
def test_register_user(api_client):
    """Test user registration API"""
    url = reverse("register")  # Reverse the URL name from urls.py
    payload = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "NewPass@123",
        "password2": "NewPass@123"
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "success"

@pytest.mark.django_db
def test_login_user(api_client, create_user):
    """Test user login API"""
    user = create_user()
    url = reverse("login")
    payload = {
        "email": user.email,
        "password": "Test@123"
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data["tokens"]

@pytest.mark.django_db
def test_login_with_wrong_password(api_client, create_user):
    """Test login with incorrect password"""
    user = create_user()
    url = reverse("login")
    payload = {
        "email": user.email,
        "password": "WrongPass@123"
    }
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_logout_user(api_client, create_user):
    """Test user logout API"""
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.force_authenticate(user=user)
    
    url = reverse("logout")
    response = api_client.post(url, {"refresh_token": str(refresh)})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == "success"