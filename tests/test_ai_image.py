import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


def create_test_image() -> bytes:
    """Create a simple test image in memory (minimal PNG)"""
    # Minimal valid PNG file (1x1 red pixel)
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'


def test_upload_image_success(client):
    """Test successful image upload and description generation"""
    # Register and login
    user_data = {
        "email": "ai_test@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "ai_test@example.com",
        "password": "testpassword123"
    }
    with patch('app.services.email.send_ip_change_alert'):
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an asset first
    asset_data = {
        "name": "Test Laptop",
        "asset_type": "laptop",
        "serial_number": "SN_AI_001",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=headers)
    asset_id = create_response.json()["id"]
    
    # Create test image
    image_data = create_test_image()
    
    # Mock OpenAI API response
    mock_description = "A red square test image. The device appears to be in good condition."
    
    with patch('app.services.ai.OpenAI') as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = mock_description
        mock_client.chat.completions.create.return_value = mock_response
        
        # Upload image
        files = {"file": ("test.png", image_data, "image/png")}
        response = client.post(
            f"/assets/{asset_id}/upload-image",
            files=files,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == mock_description
        assert data["id"] == str(asset_id)


def test_upload_image_invalid_file_type(client):
    """Test uploading non-image file fails"""
    # Register and login
    user_data = {
        "email": "ai_test2@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "ai_test2@example.com",
        "password": "testpassword123"
    }
    with patch('app.services.email.send_ip_change_alert'):
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an asset
    asset_data = {
        "name": "Test Asset",
        "asset_type": "laptop",
        "serial_number": "SN_AI_002",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=headers)
    asset_id = create_response.json()["id"]
    
    # Try to upload non-image file
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post(
        f"/assets/{asset_id}/upload-image",
        files=files,
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "image" in response.json()["detail"].lower()


def test_upload_image_file_too_large(client):
    """Test uploading image that's too large fails"""
    # Register and login
    user_data = {
        "email": "ai_test3@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "ai_test3@example.com",
        "password": "testpassword123"
    }
    with patch('app.services.email.send_ip_change_alert'):
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create an asset
    asset_data = {
        "name": "Test Asset",
        "asset_type": "laptop",
        "serial_number": "SN_AI_003",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=headers)
    asset_id = create_response.json()["id"]
    
    # Create large image (over 10MB)
    large_image = b"x" * (11 * 1024 * 1024)  # 11MB
    
    files = {"file": ("large.png", large_image, "image/png")}
    response = client.post(
        f"/assets/{asset_id}/upload-image",
        files=files,
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "size" in response.json()["detail"].lower()


def test_upload_image_nonexistent_asset(client):
    """Test uploading image for non-existent asset fails"""
    # Register and login
    user_data = {
        "email": "ai_test4@example.com",
        "password": "testpassword123"
    }
    client.post("/auth/register", json=user_data)
    
    login_data = {
        "username": "ai_test4@example.com",
        "password": "testpassword123"
    }
    with patch('app.services.email.send_ip_change_alert'):
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to upload to non-existent asset
    from uuid import uuid4
    fake_id = uuid4()
    image_data = create_test_image()
    
    files = {"file": ("test.png", image_data, "image/png")}
    response = client.post(
        f"/assets/{fake_id}/upload-image",
        files=files,
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_image_requires_auth(client):
    """Test that image upload requires authentication"""
    from uuid import uuid4
    fake_id = uuid4()
    image_data = create_test_image()
    
    files = {"file": ("test.png", image_data, "image/png")}
    response = client.post(
        f"/assets/{fake_id}/upload-image",
        files=files
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN  # HTTPBearer returns 403
