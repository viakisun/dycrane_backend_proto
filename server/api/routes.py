from fastapi import APIRouter

from server.api.routers import (
    crane_assignments,
    driver_assignments,
    attendances,
    crane_models,
    cranes,
    document_requests,
    document_items,
    health,
    owners,
    requests,
    sites,
)

api_router = APIRouter(prefix="/api/v1")

# System and catalog routes
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(
    crane_models.router, prefix="/catalog/crane-models", tags=["catalog"]
)

# Organization-related routes
api_router.include_router(sites.router, prefix="/org/sites", tags=["organization"])
api_router.include_router(cranes.router, prefix="/org/cranes", tags=["organization"])
api_router.include_router(owners.router, prefix="/org/owners", tags=["organization"])

# Operations routes
api_router.include_router(
    crane_assignments.router, prefix="/ops/crane-deployments", tags=["operations"]
)
api_router.include_router(
    driver_assignments.router, prefix="/ops/driver-deployments", tags=["operations"]
)
api_router.include_router(
    attendances.router, prefix="/ops/driver-attendance-logs", tags=["operations"]
)

# Compliance routes
api_router.include_router(
    document_requests.router, prefix="/compliance/document-requests", tags=["compliance"]
)
api_router.include_router(
    document_items.router, prefix="/compliance/document-items", tags=["compliance"]
)

# Deployment routes
api_router.include_router(
    requests.router, prefix="/deploy/requests", tags=["deployment"]
)
