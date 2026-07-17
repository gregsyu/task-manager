from pydantic_settings.main import SettingsConfigDict
from pydantic_settings import BaseSettings
from typing import List, ClassVar
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT", "development"
    )  # development | staging | production
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    PROJECT_NAME: str = "Task Manager API"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 20))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", 30))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", 3600))

    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv(
        "REFRESH_TOKEN_EXPIRE_MINUTES", 1440
    ))  # 24 hours for default

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]

    # `ClassVar` tells your code tool that a variable belongs to the class itself
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
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
