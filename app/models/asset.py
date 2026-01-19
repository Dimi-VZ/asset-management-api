from sqlalchemy import Column, String, Date, Numeric, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)
    serial_number = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="active")
    assigned_to = Column(String(255), nullable=True)
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, type={self.asset_type})>"
