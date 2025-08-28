import logging
import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db, db_manager
from server.domain.schemas import HealthCheckResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for service monitoring.
    """
    logger.debug("Health check requested")

    database_healthy = db_manager.health_check()

    response = HealthCheckResponse(
        status="healthy" if database_healthy else "degraded",
        timestamp=dt.datetime.utcnow(),
        database_healthy=database_healthy
    )

    if not database_healthy:
        logger.warning("Health check shows database connectivity issues")
    else:
        logger.debug("Health check passed")

    return response
