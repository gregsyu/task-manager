from fastapi.testclient import TestClient
from src.schemas.response import HealthResponse
from src.settings import settings
from src.main import app


def test_home_healthcheck(client: TestClient):
    response = client.get("/")
    validated = HealthResponse.model_validate(response.json())
    data = validated.model_dump()

    assert response.status_code == 200
    assert "message" in data
    assert isinstance(data["message"], str)
    assert data["version"] == app.version
    assert data["environment"] == settings.ENVIRONMENT
    """
    return {
        "message": "Task Manager API is running",
        "version": app.version,
        "environment": settings.ENVIRONMENT,
    }
    """
