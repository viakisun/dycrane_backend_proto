"""
Configuration module for DY Crane Safety Management System.
Handles environment variables, database settings, and application constants.
"""

import os
from typing import Optional
import logging


class Config:
    """Application configuration class."""
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_NAME: str = os.getenv("DB_NAME", "craneops")
    
    # Construct database URLs
    DEFAULT_PG_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_PG_URL)
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "false").lower() == "true"
    
    # Application Settings
    APP_NAME: str = "DY Crane Safety Management API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "Crane safety management system with site approval, crane assignment, "
        "attendance tracking, and document management"
    )
    
    # Database Connection Pool Settings
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    
    # File Upload Constraints
    ALLOWED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']
    REQUIRED_URL_SCHEME = "https"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def get_log_level(cls) -> int:
        """Convert string log level to logging constant."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(cls.LOG_LEVEL, logging.INFO)
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    @classmethod
    def is_testing(cls) -> bool:
        """Check if running in test mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "testing"


# Create global config instance
config = Config()