from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.auth import fastapi_users, auth_backend, get_client_ip, get_jwt_strategy
from app.services.email import send_ip_change_alert
from app.crud.users import update_user_ip, get_user_by_email
from passlib.context import CryptContext
from typing import Optional

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db=db, email=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    client_ip = get_client_ip(request)
    
    if user.last_login_ip and user.last_login_ip != client_ip:
        send_ip_change_alert(
            email=user.email,
            new_ip=client_ip,
            old_ip=user.last_login_ip
        )
    elif not user.last_login_ip:
        send_ip_change_alert(
            email=user.email,
            new_ip=client_ip,
            old_ip=None
        )
    
    update_user_ip(db=db, user_id=user.id, ip_address=client_ip)
    
    jwt_strategy = get_jwt_strategy()
    token = await jwt_strategy.write_token(user)
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    from app.crud.users import create_user
    
    try:
        user = create_user(db=db, user_create=user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
