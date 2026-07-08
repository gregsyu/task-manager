import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from .conftest import create_user, create_user_and_task
from src.main import app
from src.database import Base
from src.dependencies import get_db
from src.database import Task, User
from src.schemas.tasks import TaskCreate, TaskUpdate
from src.service import delete_task, get_task_by_id, update_task
from src.security import get_password_hash


def test_get_task_by_existing_id(db_session):
    task = create_user_and_task(db_session)
    db_session.refresh(task)

    ftask = get_task_by_id(db=db_session, task_id=task.id)
    assert ftask is not None
    assert ftask.id == task.id
    assert ftask.title == task.title
    assert ftask.description == task.description
    assert ftask.status == task.status
    assert ftask.priority == task.priority


def test_get_task_by_non_existing_id(db_session):
    task = get_task_by_id(db=db_session, task_id=999)
    assert task is None


def test_update_task(db_session):
    task = create_user_and_task(db_session)
    db_session.refresh(task)

    update_data = TaskUpdate(title="Updated Task Title", status="done")
    updated_task = update_task(db=db_session, task=task, task_update=update_data)

    assert updated_task.title == update_data.title
    assert updated_task.status == update_data.status
    # check unchanged:
    assert updated_task.description == task.description
    assert updated_task.priority == task.priority


def test_update_task_invalid_status(db_session):
    task = create_user_and_task(db_session)
    db_session.refresh(task)

    with pytest.raises(Exception) as exc_info:
        update_data = TaskUpdate(status="invalid_status")
        update_task(db=db_session, task=task, task_update=update_data)
    assert exc_info.value is not None


def test_update_task_invalid_priority(db_session):
    task = create_user_and_task(db_session)
    db_session.refresh(task)

    with pytest.raises(Exception) as exc_info:
        update_data = TaskUpdate(priority="invalid_priority")
        update_task(db=db_session, task=task, task_update=update_data)
    assert exc_info.value is not None


def test_delete_task(db_session):
    task = create_user_and_task(db_session)
    db_session.refresh(task)

    # delete the task
    delete_task(db=db_session, task=task)
    db_session.commit()

    # fetch deleted task
    deleted_task = get_task_by_id(db=db_session, task_id=task.id)
    assert deleted_task is None
