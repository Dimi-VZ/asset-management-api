from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import List, Optional
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetUpdate


def get_asset(db: Session, asset_id: UUID) -> Optional[Asset]:
    return db.query(Asset).filter(Asset.id == asset_id).first()


def get_assets(db: Session, skip: int = 0, limit: int = 100) -> List[Asset]:
    return db.query(Asset).offset(skip).limit(limit).all()


def create_asset(db: Session, asset: AssetCreate) -> Asset:
    db_asset = Asset(**asset.model_dump())
    db.add(db_asset)
    try:
        db.commit()
        db.refresh(db_asset)
        return db_asset
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Asset with serial number {asset.serial_number} already exists")


def update_asset(db: Session, asset_id: UUID, asset_update: AssetUpdate) -> Optional[Asset]:
    db_asset = get_asset(db, asset_id)
    if not db_asset:
        return None
    
    update_data = asset_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_asset, field, value)
    
    try:
        db.commit()
        db.refresh(db_asset)
        return db_asset
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Serial number {update_data.get('serial_number')} already exists")


def delete_asset(db: Session, asset_id: UUID) -> bool:
    db_asset = get_asset(db, asset_id)
    if not db_asset:
        return False
    
    db.delete(db_asset)
    db.commit()
    return True
