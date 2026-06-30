"""Общие фикстуры для тестов.

Используется изолированная SQLite-БД в файле, чтобы не требовать PostgreSQL
во время прогона pytest (в CI и локально).
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.cart import Cart
from app.models.user import User, UserRole

# In-memory SQLite, общий для всех соединений через StaticPool.
engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    # Свежая сессия на каждый запрос — как в реальном приложении (get_db).
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session) -> User:
    user = User(
        email="admin@test.com",
        full_name="Admin",
        hashed_password=hash_password("admin12345"),
        role=UserRole.admin,
    )
    user.cart = Cart()
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    resp = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        data={"username": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user) -> dict[str, str]:
    return _auth_header(client, "admin@test.com", "admin12345")


@pytest.fixture
def customer_headers(client) -> dict[str, str]:
    client.post(
        f"{settings.API_V1_PREFIX}/auth/register",
        json={
            "email": "customer@test.com",
            "full_name": "Customer",
            "password": "customer12345",
        },
    )
    return _auth_header(client, "customer@test.com", "customer12345")
