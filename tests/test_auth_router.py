import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from .conftest import create_user
from src.main import app
from src.database import Base
from src.dependencies import get_db, get_current_user
from src.schemas.auth import UserCreate, Token
from src.security import get_password_hash
from src.database import User


@pytest.fixture(scope="function")
def auth_client(client, db_session):
    db_user = create_user(db_session)

    app.dependency_overrides[get_current_user] = lambda: db_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


def test_register_user_success(client, db_session):
    user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="strongpassword123",
        full_name="Test User da Silva",
    )
    user_data = user_data.model_dump()

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data


def test_register_user_already_exists(client, db_session):
    # create existing user first
    create_user(db_session, username="existing", email="existing@example.com")

    user_data = {
        "username": "existing",
        "email": "existing@example.com",
        "password": "password123",
        "full_name": "Existing User",
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


def test_login_success(client, db_session):
    create_user(db_session, username="testuser")

    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, db_session):
    create_user(db_session, username="testuser")

    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


def test_read_users_me(auth_client):
    response = auth_client.get("/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"


def test_read_users_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
