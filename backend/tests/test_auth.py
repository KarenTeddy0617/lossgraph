import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user import User


# =========================================================
# Test database
# =========================================================

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Only the User table is required for these authentication tests.
User.__table__.create(bind=engine, checkfirst=True)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# =========================================================
# Tests
# =========================================================

def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "LossGraph API is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert "id" in data

    # Password must never be returned.
    assert "hashed_password" not in data
    assert "password" not in data


def test_duplicate_username():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicateuser",
            "email": "duplicate1@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "duplicateuser",
            "email": "duplicate2@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_duplicate_email():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "emailuser1",
            "email": "same@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "emailuser2",
            "email": "same@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_login():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrongpassuser",
            "email": "wrongpass@example.com",
            "password": "correctpassword",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrongpassuser",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_me_requires_authentication():
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me():
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "meuser",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"
