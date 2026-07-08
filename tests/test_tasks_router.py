import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from .conftest import create_user
from src.main import app
from src.database import Base
from src.dependencies import get_db
from src.schemas.tasks import TaskCreate, TaskUpdate
from src.schemas.auth import UserCreate
from src.security import get_password_hash
from src.database import User


@pytest.fixture(scope="function")  # mocks JWT
def auth_client(client, db_session):
    from src.dependencies import get_current_user

    test_user = create_user(db_session)
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)  # clean up override


def test_create_task(auth_client, db_session):
    from src.dependencies import get_current_user

    task_data = TaskCreate(
        title="Test Task",
        description="This is a test task",
        status="pending",
        priority="medium",
    )
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data.title
    assert data["description"] == task_data.description
    assert data["status"] == task_data.status
    assert data["priority"] == task_data.priority
    assert "id" in data


def test_read_tasks(auth_client, db_session):
    from src.dependencies import get_current_user

    # create a task first
    task_data = TaskCreate(title="Test Task 2", description="Another test task")
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201

    # read the tasks
    response = auth_client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == task_data.title


def test_read_task_by_id(auth_client, db_session):
    from src.dependencies import get_current_user

    # create a task
    task_data = TaskCreate(title="Test Task 3", description="Task for reading by id")
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    task_id = response.json()["id"]

    # read the task by id
    response = auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == task_data.title


def test_update_task(auth_client, db_session):
    from src.dependencies import get_current_user

    # create a task
    task_data = TaskCreate(title="Test Task 4", description="Task to update")
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    task_id = response.json()["id"]

    # update the task
    update_data = TaskUpdate(title="Updated Task Title", status="done")
    response = auth_client.patch(
        f"/tasks/{task_id}", json=update_data.model_dump(exclude_unset=True)
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data.title
    assert data["status"] == update_data.status


def test_delete_task(auth_client, db_session):
    from src.dependencies import get_current_user

    # create a task
    task_data = TaskCreate(title="Test Task 5", description="Task to delete")
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    task_id = response.json()["id"]

    # delete the task
    response = auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # verify it's deleted
    response = auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
