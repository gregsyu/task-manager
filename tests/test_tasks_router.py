import pytest
from .conftest import create_user
from src.main import app
from src.schemas.tasks import (
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from typing import List
from pydantic import TypeAdapter


@pytest.fixture(scope="function")  # mocks JWT
def auth_client(client: TestClient, db_session: Session):
    from src.dependencies import get_current_user

    test_user = create_user(db_session)
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    _ = app.dependency_overrides.pop(get_current_user, None)  # clean up override


def test_create_task(auth_client: TestClient):
    task_data = TaskCreate(
        title="Test Task",
        description="This is a test task",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    data = TaskResponse.model_validate(response.json())
    assert data.title == task_data.title
    assert data.description == task_data.description
    assert data.status == task_data.status
    assert data.priority == task_data.priority
    assert data.id is not None


def test_read_tasks(auth_client: TestClient):
    # create a task first
    task_data = TaskCreate(
        title="Test Task 2", description="Another test task", status=TaskStatus.PENDING
    )
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201

    # read the tasks
    response = auth_client.get("/tasks/")
    assert response.status_code == 200
    data = TypeAdapter(List[TaskResponse]).validate_python(response.json())
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0].title == task_data.title


def test_read_task_by_id(auth_client: TestClient):
    # create a task
    task_data = TaskCreate(
        title="Test Task 3",
        description="Task for reading by id",
        status=TaskStatus.PENDING,
    )
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    task_id = TaskResponse.model_validate(response.json()).id

    # read the task by id
    response = auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = TaskResponse.model_validate(response.json())
    assert data.id == task_id
    assert data.title == task_data.title


def test_update_task(auth_client: TestClient):
    # create a task
    task_data = TaskCreate(
        title="Test Task 4", description="Task to update", status=TaskStatus.PENDING
    )
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    task_id = TaskResponse.model_validate(response.json()).id

    # update the task
    update_data = TaskUpdate(title="Updated Task Title", status=TaskStatus.DONE)
    response = auth_client.patch(
        f"/tasks/{task_id}", json=update_data.model_dump(exclude_unset=True)
    )
    assert response.status_code == 200
    data = TaskResponse.model_validate(response.json())
    assert data.title == update_data.title
    assert data.status == update_data.status


def test_delete_task(auth_client: TestClient):
    # create a task
    task_data = TaskCreate(
        title="Test Task 5", description="Task to delete", status=TaskStatus.PENDING
    )
    response = auth_client.post("/tasks/", json=task_data.model_dump())
    assert response.status_code == 201
    task_id = TaskResponse.model_validate(response.json()).id

    # delete the task
    response = auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # verify it's deleted
    response = auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
