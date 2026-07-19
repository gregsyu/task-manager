from fastapi.testclient import TestClient
import pytest
from src.schemas.response import ErrorResponse
from .conftest import create_user
from src.main import app
from src.dependencies import get_current_user
from src.schemas.auth import UserCreate, Token, UserOut
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def auth_client(client: TestClient, db_session: Session):
    db_user = create_user(db_session)

    app.dependency_overrides[get_current_user] = lambda: db_user
    yield client
    _ = app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.usefixtures("db_session")  # tell pytest to run the fixture without injecting it
def test_register_user_success(client: TestClient):
    user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="strongpassword123",
        full_name="Test User da Silva",
    )
    user_data = user_data.model_dump()

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    data = UserOut.model_validate(response.json())
    assert data.username == user_data["username"]
    assert data.email == user_data["email"]
    assert data.id is not None


def test_register_user_already_exists(client: TestClient, db_session: Session):
    # create existing user first
    _ = create_user(db_session, username="existing", email="existing@example.com")

    user_data = {
        "username": "existing",
        "email": "existing@example.com",
        "password": "password123",
        "full_name": "Existing User",
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 400
    assert "already exists" in ErrorResponse.model_validate(response.json()).detail.lower()


def test_login_success(client: TestClient, db_session: Session):
    _ = create_user(db_session, username="testuser")

    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = Token.model_validate(response.json()).model_dump()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, db_session: Session):
    _ = create_user(db_session, username="testuser")

    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
    assert "invalid credentials" in ErrorResponse.model_validate(response.json()).detail.lower()


def test_read_users_me(auth_client: TestClient):
    response = auth_client.get("/auth/me")

    assert response.status_code == 200
    # data = response.json()
    data = UserOut.model_validate(response.json())
    assert data.username == "testuser"
    assert data.email == "testuser@example.com"


def test_read_users_me_unauthorized(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
