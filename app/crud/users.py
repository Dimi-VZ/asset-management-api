from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import Optional
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    existing_user = get_user_by_email(db, user_create.email)
    if existing_user:
        raise ValueError(f"User with email {user_create.email} already exists")
    
    hashed_password = pwd_context.hash(user_create.password)
    
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError(f"User with email {user_create.email} already exists")


def update_user_ip(db: Session, user_id: UUID, ip_address: str) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.last_login_ip = ip_address
    db.commit()
    db.refresh(db_user)
    return db_user
