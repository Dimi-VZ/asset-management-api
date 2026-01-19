from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class AssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(..., min_length=1, max_length=100)
    serial_number: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="active", max_length=50)
    assigned_to: Optional[str] = Field(None, max_length=255)
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    asset_type: Optional[str] = Field(None, min_length=1, max_length=100)
    serial_number: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    assigned_to: Optional[str] = Field(None, max_length=255)
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None


class AssetResponse(AssetBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
