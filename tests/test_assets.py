import pytest
from uuid import uuid4
from fastapi import status
from app.schemas.asset import AssetCreate


def test_create_asset(client, auth_headers):
    """Test creating a new asset"""
    asset_data = {
        "name": "MacBook Pro",
        "asset_type": "laptop",
        "serial_number": "SN123456",
        "status": "active",
        "assigned_to": "John Doe",
        "purchase_date": "2024-01-15",
        "purchase_price": 2499.99,
        "description": "16-inch MacBook Pro"
    }
    response = client.post("/assets", json=asset_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == asset_data["name"]
    assert data["asset_type"] == asset_data["asset_type"]
    assert data["serial_number"] == asset_data["serial_number"]
    assert "id" in data
    assert "created_at" in data


def test_create_asset_duplicate_serial(client, auth_headers):
    """Test creating asset with duplicate serial number fails"""
    asset_data = {
        "name": "MacBook Pro",
        "asset_type": "laptop",
        "serial_number": "SN123456",
        "status": "active"
    }
    # Create first asset
    client.post("/assets", json=asset_data, headers=auth_headers)
    # Try to create duplicate
    response = client.post("/assets", json=asset_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_assets(client, auth_headers):
    """Test listing all assets"""
    # Create some assets
    assets = [
        {
            "name": "MacBook Pro",
            "asset_type": "laptop",
            "serial_number": "SN001",
            "status": "active"
        },
        {
            "name": "Dell Monitor",
            "asset_type": "monitor",
            "serial_number": "SN002",
            "status": "active"
        }
    ]
    for asset in assets:
        client.post("/assets", json=asset, headers=auth_headers)
    
    response = client.get("/assets", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    assert any(a["serial_number"] == "SN001" for a in data)
    assert any(a["serial_number"] == "SN002" for a in data)


def test_get_asset_by_id(client, auth_headers):
    """Test getting an asset by ID"""
    asset_data = {
        "name": "iPhone 15",
        "asset_type": "phone",
        "serial_number": "SN003",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=auth_headers)
    asset_id = create_response.json()["id"]
    
    response = client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == asset_id
    assert data["name"] == asset_data["name"]


def test_get_asset_not_found(client, auth_headers):
    """Test getting non-existent asset returns 404"""
    fake_id = str(uuid4())
    response = client.get(f"/assets/{fake_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_asset(client, auth_headers):
    """Test updating an asset"""
    asset_data = {
        "name": "MacBook Pro",
        "asset_type": "laptop",
        "serial_number": "SN004",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=auth_headers)
    asset_id = create_response.json()["id"]
    
    update_data = {
        "name": "MacBook Pro Updated",
        "status": "maintenance"
    }
    response = client.put(f"/assets/{asset_id}", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["status"] == update_data["status"]
    assert data["serial_number"] == asset_data["serial_number"]  # Unchanged


def test_update_asset_not_found(client, auth_headers):
    """Test updating non-existent asset returns 404"""
    fake_id = str(uuid4())
    update_data = {"name": "Updated Name"}
    response = client.put(f"/assets/{fake_id}", json=update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_asset(client, auth_headers):
    """Test deleting an asset"""
    asset_data = {
        "name": "Test Asset",
        "asset_type": "laptop",
        "serial_number": "SN005",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=auth_headers)
    asset_id = create_response.json()["id"]
    
    response = client.delete(f"/assets/{asset_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify asset is deleted
    get_response = client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_asset_not_found(client, auth_headers):
    """Test deleting non-existent asset returns 404"""
    fake_id = str(uuid4())
    response = client.delete(f"/assets/{fake_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_assets_pagination(client, auth_headers):
    """Test listing assets with pagination"""
    # Create multiple assets
    for i in range(5):
        asset_data = {
            "name": f"Asset {i}",
            "asset_type": "laptop",
            "serial_number": f"SN{i:03d}",
            "status": "active"
        }
        client.post("/assets", json=asset_data, headers=auth_headers)
    
    # Test pagination
    response = client.get("/assets?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
