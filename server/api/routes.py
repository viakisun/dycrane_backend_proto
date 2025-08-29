from fastapi import APIRouter

from server.api.routers import health, sites, cranes, assignments, documents

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(cranes.router, tags=["cranes"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(documents.router, prefix="/docs", tags=["documents"])