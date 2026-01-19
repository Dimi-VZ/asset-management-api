from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from app.crud import assets as crud
from app.cache import get_cache, set_cache, delete_cache, cache_key
from app.auth import current_active_user
from app.models.user import User
from app.services.ai import generate_asset_description

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    try:
        created_asset = crud.create_asset(db=db, asset=asset)
        from app.cache import invalidate_pattern
        invalidate_pattern("assets:list*")
        return created_asset
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[AssetResponse])
def list_assets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    cache_key_str = cache_key("assets:list", skip=skip, limit=limit)
    
    cached_assets = get_cache(cache_key_str)
    if cached_assets is not None:
        return [AssetResponse(**asset) for asset in cached_assets]
    
    assets = crud.get_assets(db=db, skip=skip, limit=limit)
    assets_response = [AssetResponse.model_validate(asset) for asset in assets]
    assets_dict = [asset.model_dump(mode='json') for asset in assets_response]
    
    set_cache(cache_key_str, assets_dict, ttl=60)
    
    return assets_response


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    asset = crud.get_asset(db=db, asset_id=asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: UUID,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    try:
        asset = crud.update_asset(db=db, asset_id=asset_id, asset_update=asset_update)
        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with id {asset_id} not found"
            )
        from app.cache import invalidate_pattern
        invalidate_pattern("assets:list*")
        delete_cache(cache_key("assets", asset_id=str(asset_id)))
        return asset
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    success = crud.delete_asset(db=db, asset_id=asset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
    from app.cache import invalidate_pattern
    invalidate_pattern("assets:list*")
    delete_cache(cache_key("assets", asset_id=str(asset_id)))
    return None


@router.post("/{asset_id}/upload-image", response_model=AssetResponse)
async def upload_asset_image(
    asset_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    file_contents = await file.read()
    if len(file_contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file size must be less than 10MB"
        )
    
    asset = crud.get_asset(db=db, asset_id=asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with id {asset_id} not found"
        )
    
    image_format = "png"
    if file.content_type == "image/jpeg" or file.content_type == "image/jpg":
        image_format = "jpeg"
    elif file.content_type == "image/png":
        image_format = "png"
    else:
        if file.filename:
            ext = file.filename.split(".")[-1].lower()
            if ext in ["jpg", "jpeg"]:
                image_format = "jpeg"
            elif ext == "png":
                image_format = "png"
    
    try:
        description = generate_asset_description(file_contents, image_format)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    asset_update = AssetUpdate(description=description)
    updated_asset = crud.update_asset(db=db, asset_id=asset_id, asset_update=asset_update)
    
    if not updated_asset:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update asset description"
        )
    
    delete_cache("assets:list")
    delete_cache(cache_key("assets", asset_id=str(asset_id)))
    
    return updated_asset
