from src.settings import Settings


def test_settings_default_values():
    settings = Settings(
        _env_file=None,
        SECRET_KEY="test-secret",
        DATABASE_URL="sqlite:///test.db",
    )

    assert settings.PROJECT_NAME == "Task Manager API"
    assert settings.PROJECT_VERSION == "0.1.0"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 1440
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert isinstance(settings.CORS_ORIGINS, list)
    assert isinstance(settings.DEBUG, bool)

    assert settings.DB_POOL_SIZE == 20
    assert settings.DB_MAX_OVERFLOW == 10
    assert settings.DB_POOL_TIMEOUT == 30
    assert settings.DB_POOL_RECYCLE == 3600
