from fastapi import APIRouter

from server.api.routers import (
    crane_assignments,
    driver_assignments,
    attendances,
    crane_models,
    cranes,
    documents,
    health,
    owners,
    requests,
    sites,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(cranes.router, prefix="/cranes", tags=["cranes"])
api_router.include_router(
    crane_models.router, prefix="/crane-models", tags=["crane-models"]
)
api_router.include_router(owners.router, prefix="/owners", tags=["owners"])
api_router.include_router(
    crane_assignments.router, prefix="/crane-assignments", tags=["crane-assignments"]
)
api_router.include_router(
    driver_assignments.router,
    prefix="/driver-assignments",
    tags=["driver-assignments"],
)
api_router.include_router(
    attendances.router, prefix="/attendances", tags=["attendances"]
)
api_router.include_router(documents.router, prefix="/docs", tags=["documents"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
