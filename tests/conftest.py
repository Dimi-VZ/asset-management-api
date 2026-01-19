import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.config import settings
from app.crud.users import create_user
from app.schemas.user import UserCreate
from app.auth import get_jwt_strategy
from app.models.user import User

SQLALCHEMY_TEST_DATABASE_URL = "postgresql://assetuser:assetpass@postgres:5432/assetdb"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    pool_pre_ping=True
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    user_create = UserCreate(
        email="testuser@example.com",
        password="testpassword123"
    )
    user = create_user(db=db_session, user_create=user_create)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user):
    from jose import jwt
    from app.config import settings
    from datetime import datetime, timedelta
    
    payload = {
        "sub": str(test_user.id),
        "aud": ["fastapi-users:auth"],
        "exp": datetime.utcnow() + timedelta(seconds=settings.jwt_lifetime_seconds)
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


@pytest.fixture(scope="function")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
