from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development | staging | production
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    PROJECT_NAME: str = "Task Manager API"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # Alternativa async (se usar SQLAlchemy async):
    # DATABASE_URL: str = "mysql+aiomysql://user:password@localhost:3306/task_manager"

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", ".env.development"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ("production", "prod")


settings = Settings()


if __name__ == "__main__" and settings.DEBUG:
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"CORS Origins: {settings.CORS_ORIGINS}")