import datetime as dt
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import db_manager, get_db
from server.domain.schemas import HealthCheckResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=HealthCheckResponse)
def health_check_endpoint(db: Session = Depends(get_db)):
    """
    Health check endpoint for service monitoring.
    """
    logger.debug("Health check requested")

    database_healthy = db_manager.health_check()

    response = HealthCheckResponse(
        status="healthy" if database_healthy else "degraded",
        timestamp=dt.datetime.utcnow(),
        database_healthy=database_healthy,
    )

    if not database_healthy:
        logger.warning("Health check shows database connectivity issues")
    else:
        logger.debug("Health check passed")

    return response


@router.post("/tools/reset-transactional", status_code=204)
def reset_transactional_data_endpoint():
    """
    Reset only the transactional data in the database.
    Preserves master data like users, cranes, etc.
    """
    logger.info("Received request to reset transactional data")
    try:
        db_manager.reset_transactional_data()
    except Exception as e:
        logger.error(f"An error occurred during transactional data reset: {e}")
        raise


@router.post("/tools/reset-full", status_code=204)
def reset_full_database_for_testing_endpoint():
    """
    Reset the entire database. FOR DEVELOPMENT/TESTING ONLY.
    WARNING: This is a destructive operation.
    """
    logger.warning("Received request for a full database reset")
    try:
        db_manager.reset_full_database()
    except Exception as e:
        logger.error(f"An error occurred during full database reset: {e}")
        raise
