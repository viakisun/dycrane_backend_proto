"""
Database connection and session management for DY Crane Safety Management System.
Handles SQLAlchemy engine configuration, session lifecycle, and database events.
"""

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from config import config

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy base for model definitions
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = Base  # Make Base accessible through the manager
        self._initialize_engine()
        self._setup_events()
    
    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with configuration."""
        try:
            self.engine = create_engine(
                config.DATABASE_URL,
                future=True,
                echo=config.DB_ECHO,
                pool_pre_ping=config.DB_POOL_PRE_PING,
                pool_recycle=config.DB_POOL_RECYCLE
            )
            
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autoflush=False,
                autocommit=False,
                future=True
            )
            
            logger.info(
                "Database engine initialized successfully",
                extra={
                    "database_url": config.DATABASE_URL.split('@')[1] if '@' in config.DATABASE_URL else config.DATABASE_URL,
                    "pool_recycle": config.DB_POOL_RECYCLE,
                    "echo": config.DB_ECHO
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _setup_events(self) -> None:
        """Set up database event listeners."""
        if self.engine:
            @event.listens_for(self.engine, "connect")
            def _set_search_path(dbapi_conn, conn_record):
                """Set PostgreSQL search path to ops schema for all connections."""
                try:
                    with dbapi_conn.cursor() as cur:
                        cur.execute("SET search_path TO ops, public;")
                    logger.debug("Search path set to 'ops, public' for new connection")
                except Exception as e:
                    logger.warning(f"Failed to set search path: {e}")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Ensures proper session cleanup and error handling.
        """
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        
        session = self.SessionLocal()
        try:
            yield session
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error occurred: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error in database session: {e}")
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """
        Check database connectivity and basic functionality.
        Returns True if database is healthy, False otherwise.
        """
        try:
            with self.get_session() as session:
                # Simple query to test connectivity
                result = session.execute("SELECT 1 as health_check")
                return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self) -> None:
        """Close database connections and clean up resources."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Create global database manager instance
db_manager = DatabaseManager()

# Convenience function for FastAPI dependency injection
def get_db():
    """Database session dependency for FastAPI endpoints."""
    if not db_manager.SessionLocal:
        raise RuntimeError("Database not initialized")
    
    session = db_manager.SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()