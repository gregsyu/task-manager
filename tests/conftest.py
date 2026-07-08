import pytest
from src.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from src.dependencies import get_db
from src.database import Base, User
from src.security import get_password_hash
from src.database import Task

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


def create_user(db_session, **kwargs):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": get_password_hash("password123"),
        "full_name": "Test user pereira",
    }
    data.update(kwargs)

    user = User(**data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_user_and_task(db_session, **kwargs):
    user = create_user(db_session)
    data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium",
        "owner_id": user.id,
    }
    data.update(kwargs)

    db_task = Task(**data)
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)
    return db_task
