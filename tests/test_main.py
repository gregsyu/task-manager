from src.settings import settings
from src.main import app


def test_home_healthcheck(client):
    response = client.get("/")
    data = response.json()

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
