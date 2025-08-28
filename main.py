"""
Main application entry point for DY Crane Safety Management System.
Configures FastAPI app, logging, and starts the development server.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from config import config
from database import db_manager
from routes import router


def configure_logging():
    """Configure application logging with appropriate formatters and levels."""
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.get_log_level())
    
    # Clear existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(config.get_log_level())
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING if not config.is_development() else logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not config.DB_ECHO else logging.INFO)
    
    # Log startup configuration
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Level: {config.LOG_LEVEL}, Environment: {config.is_development() and 'development' or 'production'}"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown procedures.
    """
    logger = logging.getLogger(__name__)
    
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info("=" * 60)
    
    # Database health check
    if db_manager.health_check():
        logger.info("Database connectivity verified")
    else:
        logger.error("Database connectivity check failed")
        logger.warning("Application starting anyway - check database configuration")
    
    logger.info(f"API server ready at http://{config.API_HOST}:{config.API_PORT}")
    logger.info(f"Documentation available at http://{config.API_HOST}:{config.API_PORT}/docs")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    db_manager.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    app = FastAPI(
        title=config.APP_NAME,
        description=config.APP_DESCRIPTION,
        version=config.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if config.is_development() else None,
        redoc_url="/redoc" if config.is_development() else None,
    )
    
    # CORS middleware for development
    if config.is_development():
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Include API routes
    app.include_router(router)
    
    # Root redirect to documentation
    @app.get("/", include_in_schema=False)
    async def root():
        """Redirect root requests to API documentation."""
        return RedirectResponse(url="/docs")
    
    return app


# Configure logging before creating the app
configure_logging()

# Create application instance
app = create_app()

# Application startup logging
logger = logging.getLogger(__name__)
logger.info(f"Application module loaded - {config.APP_NAME} v{config.APP_VERSION}")


def main():
    """
    Main function for direct script execution.
    Starts the uvicorn development server.
    """
    import uvicorn
    
    logger.info("Starting development server...")
    logger.info(f"Server configuration: {config.API_HOST}:{config.API_PORT} (reload={config.API_RELOAD})")
    
    try:
        uvicorn.run(
            "main:app",
            host=config.API_HOST,
            port=config.API_PORT,
            log_level=config.LOG_LEVEL.lower(),
            reload=config.API_RELOAD,
            access_log=config.is_development()
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()