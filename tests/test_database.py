from src.database import Base, Task, User
from src.schemas.tasks import TaskStatus, TaskPriority
from .conftest import create_user, create_user_and_task
from sqlalchemy.orm import Session


def test_database_models_import():
    assert Base is not None
    assert Task is not None
    assert User is not None


def test_task_model_creation(db_session: Session):
    task = create_user_and_task(
        db_session,
        title="Test Task",
        description="This is a test task",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )

    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.MEDIUM
    assert task.owner.username == "testuser"


def test_user_model_creation(db_session: Session):
    user = create_user(
        db_session,
        username="testuser2",
        email="test2@example.com",
        hashed_password="hashedpassword2",
        full_name="Test User 2",
    )

    assert user.id is not None
    assert user.username == "testuser2"
    assert user.email == "test2@example.com"
    assert user.hashed_password == "hashedpassword2"
    assert user.full_name == "Test User 2"
