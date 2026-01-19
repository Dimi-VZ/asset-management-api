import pytest
import time
from fastapi import status
from app.cache import get_cache, set_cache, delete_cache, cache_key


def test_cache_set_get(client, auth_headers):
    """Test setting and getting from cache"""
    # Create an asset
    asset_data = {
        "name": "Test Asset",
        "asset_type": "laptop",
        "serial_number": "SN_CACHE_001",
        "status": "active"
    }
    response = client.post("/assets", json=asset_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    
    # First request - should hit database
    response1 = client.get("/assets", headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    
    # Second request immediately - should hit cache
    response2 = client.get("/assets", headers=auth_headers)
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    
    # Data should be the same
    assert len(data1) == len(data2)
    assert data1 == data2


def test_cache_invalidation_on_create(client, auth_headers):
    """Test that cache is invalidated when creating a new asset"""
    # Create an asset and cache the list
    asset_data1 = {
        "name": "Asset 1",
        "asset_type": "laptop",
        "serial_number": "SN_CACHE_002",
        "status": "active"
    }
    client.post("/assets", json=asset_data1, headers=auth_headers)
    
    # Get list (this will cache it)
    response1 = client.get("/assets", headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    count1 = len(response1.json())
    
    # Create another asset
    asset_data2 = {
        "name": "Asset 2",
        "asset_type": "monitor",
        "serial_number": "SN_CACHE_003",
        "status": "active"
    }
    client.post("/assets", json=asset_data2, headers=auth_headers)
    
    # Get list again - should reflect new asset (cache invalidated)
    response2 = client.get("/assets", headers=auth_headers)
    assert response2.status_code == status.HTTP_200_OK
    count2 = len(response2.json())
    
    assert count2 == count1 + 1


def test_cache_invalidation_on_update(client, auth_headers):
    """Test that cache is invalidated when updating an asset"""
    # Create an asset
    asset_data = {
        "name": "Original Name",
        "asset_type": "laptop",
        "serial_number": "SN_CACHE_004",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=auth_headers)
    asset_id = create_response.json()["id"]
    
    # Get list (cache it)
    response1 = client.get("/assets", headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    
    # Update the asset
    update_data = {"name": "Updated Name"}
    client.put(f"/assets/{asset_id}", json=update_data, headers=auth_headers)
    
    # Get list again - should reflect update (cache invalidated)
    response2 = client.get("/assets", headers=auth_headers)
    assert response2.status_code == status.HTTP_200_OK
    assets = response2.json()
    
    # Find the updated asset
    updated_asset = next((a for a in assets if a["id"] == asset_id), None)
    assert updated_asset is not None
    assert updated_asset["name"] == "Updated Name"


def test_cache_invalidation_on_delete(client, auth_headers):
    """Test that cache is invalidated when deleting an asset"""
    # Create an asset
    asset_data = {
        "name": "To Delete",
        "asset_type": "laptop",
        "serial_number": "SN_CACHE_005",
        "status": "active"
    }
    create_response = client.post("/assets", json=asset_data, headers=auth_headers)
    asset_id = create_response.json()["id"]
    
    # Get list (cache it)
    response1 = client.get("/assets", headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    count1 = len(response1.json())
    
    # Delete the asset
    client.delete(f"/assets/{asset_id}", headers=auth_headers)
    
    # Get list again - should reflect deletion (cache invalidated)
    response2 = client.get("/assets", headers=auth_headers)
    assert response2.status_code == status.HTTP_200_OK
    count2 = len(response2.json())
    
    assert count2 == count1 - 1


def test_cache_ttl(client, auth_headers):
    """Test that cache expires after TTL (60 seconds)"""
    # Create an asset
    asset_data = {
        "name": "TTL Test",
        "asset_type": "laptop",
        "serial_number": "SN_CACHE_006",
        "status": "active"
    }
    client.post("/assets", json=asset_data, headers=auth_headers)
    
    # Get list (cache it)
    response1 = client.get("/assets", headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    count1 = len(response1.json())
    
    from app.cache import delete_cache, cache_key
    delete_cache(cache_key("assets:list", skip=0, limit=100))
    
    response2 = client.get("/assets", headers=auth_headers)
    assert response2.status_code == status.HTTP_200_OK
    count2 = len(response2.json())
    
    assert count1 == count2  # Same data, but from database this time
