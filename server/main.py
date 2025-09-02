"""
Main application entry point for DY Crane Safety Management System.
Configures FastAPI app, logging, and starts the development server.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from server.api.routes import api_router
from server.config import settings
from server.database import db_manager


def configure_logging():
    """Configure application logging with appropriate formatters and levels."""

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.get_log_level())

    # Clear existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.get_log_level())
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(
        logging.WARNING if not settings.is_development() else logging.INFO
    )
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DB_ECHO else logging.INFO
    )

    # Log startup configuration
    logger = logging.getLogger(__name__)
    logger.info(
        (
            f"Logging configured - Level: {settings.LOG_LEVEL}, Environment: "
            f"{settings.is_development() and 'development' or 'production'}"
        )
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
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    # Database health check
    if db_manager.health_check():
        logger.info("Database connectivity verified")
    else:
        logger.error("Database connectivity check failed")
        logger.warning("Application starting anyway - check database configuration")

    logger.info(f"API server ready at http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(
        f"Documentation available at http://{settings.API_HOST}:{settings.API_PORT}/docs"
    )

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
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
    )

    # CORS middleware for development
    if settings.is_development():
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Global error handling middleware
    @app.middleware("http")
    async def log_server_errors(request, call_next):
        logger = logging.getLogger(__name__)
        try:
            return await call_next(request)
        except Exception as e:
            logger.error("="*30)
            logger.error(f"Unhandled server error: {e}", exc_info=True)
            logger.error("="*30)
            return JSONResponse(
                status_code=500,
                content={"detail": "An internal server error occurred."},
            )

    # Include API routes
    app.include_router(api_router)

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
logger.info(f"Application module loaded - {settings.APP_NAME} v{settings.APP_VERSION}")


def main():
    """
    Main function for direct script execution.
    Starts the uvicorn development server.
    """
    import uvicorn

    logger.info("Starting development server...")
    logger.info(
        f"Server configuration: {settings.API_HOST}:{settings.API_PORT} "
        f"(reload={settings.API_RELOAD})"
    )

    try:
        uvicorn.run(
            "server.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level=settings.LOG_LEVEL.lower(),
            reload=settings.API_RELOAD,
            access_log=settings.is_development(),
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
