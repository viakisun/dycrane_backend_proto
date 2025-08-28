import logging
from functools import lru_cache
from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application Settings
    APP_NAME: str = "DY Crane Safety Management API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Crane safety management system"
    ENVIRONMENT: str = "development"

    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    E2E_BASE_URL: str = "http://127.0.0.1:8000"

    # Database Configuration
    PGHOST: str
    PGPORT: int = 5432
    PGUSER: str
    PGPASSWORD: str
    PGDATABASE: str

    # SQLAlchemy specific settings
    DB_ECHO: bool = False
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 3600

    @property
    def DATABASE_URL(self) -> str:
        """Construct SQLAlchemy database URL."""
        return f"postgresql+psycopg2://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"

    # File Upload Constraints
    ALLOWED_FILE_EXTENSIONS: Set[str] = {".pdf", ".jpg", ".jpeg", ".png"}
    REQUIRED_URL_SCHEME: str = "https"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    def get_log_level(self) -> int:
        """Convert string log level to logging constant."""
        return logging.getLevelName(self.LOG_LEVEL.upper())

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"

    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.ENVIRONMENT.lower() == "test"


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the Settings object."""
    return Settings()


# Global settings instance for easy access
settings = get_settings()