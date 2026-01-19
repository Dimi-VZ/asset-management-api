import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from app.services.email import send_ip_change_alert


def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data  # Password should not be in response


def test_register_duplicate_email(client):
    """Test registering with duplicate email fails"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123"
    }
    # Register first user
    client.post("/auth/register", json=user_data)
    # Try to register again
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(client):
    """Test successful login"""
    # Register user first
    user_data = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": "login@example.com",  # FastAPI Users uses "username" for email
        "password": "testpassword123"
    }
    with patch('app.api.routes.auth.send_ip_change_alert') as mock_email:
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # First login should trigger email (no previous IP)
        assert mock_email.called


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_wrong_password(client):
    """Test login with wrong password"""
    # Register user first
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    # Try to login with wrong password
    login_data = {
        "username": "wrongpass@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_ip_tracking_on_login(client):
    """Test that IP is tracked and email sent on IP change"""
    # Register user
    user_data = {
        "email": "iptest@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    # First login
    login_data = {
        "username": "iptest@example.com",
        "password": "testpassword123"
    }
    with patch('app.api.routes.auth.send_ip_change_alert') as mock_email:
        response = client.post("/auth/login", data=login_data, headers={"X-Forwarded-For": "192.168.1.1"})
        assert response.status_code == status.HTTP_200_OK
        # First login should trigger email
        assert mock_email.called
        mock_email.reset_mock()
    
    # Second login with same IP - should not send email
    with patch('app.api.routes.auth.send_ip_change_alert') as mock_email:
        response = client.post("/auth/login", data=login_data, headers={"X-Forwarded-For": "192.168.1.1"})
        assert response.status_code == status.HTTP_200_OK
        # Same IP should not trigger email
        assert not mock_email.called
    
    # Third login with different IP - should send email
    with patch('app.api.routes.auth.send_ip_change_alert') as mock_email:
        response = client.post("/auth/login", data=login_data, headers={"X-Forwarded-For": "192.168.1.2"})
        assert response.status_code == status.HTTP_200_OK
        # Different IP should trigger email
        assert mock_email.called
        # Verify email was called with correct parameters
        call_args = mock_email.call_args
        assert call_args[1]["new_ip"] == "192.168.1.2"
        assert call_args[1]["old_ip"] == "192.168.1.1"


def test_protected_endpoints_require_auth(client):
    """Test that asset endpoints require authentication"""
    # Try to access without token
    response = client.get("/assets")
    assert response.status_code == status.HTTP_403_FORBIDDEN  # HTTPBearer returns 403
    
    response = client.post("/assets", json={
        "name": "Test",
        "asset_type": "laptop",
        "serial_number": "SN001",
        "status": "active"
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN  # HTTPBearer returns 403


def test_protected_endpoints_with_auth(client):
    """Test that asset endpoints work with valid token"""
    # Register and login
    user_data = {
        "email": "authtest@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "authtest@example.com",
        "password": "testpassword123"
    }
    with patch('app.api.routes.auth.send_ip_change_alert'):
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
    
    # Access protected endpoint with token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/assets", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Create asset with token
    asset_data = {
        "name": "Test Asset",
        "asset_type": "laptop",
        "serial_number": "SN_AUTH_001",
        "status": "active"
    }
    response = client.post("/assets", json=asset_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
