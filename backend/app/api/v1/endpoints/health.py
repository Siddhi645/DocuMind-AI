"""
DocuMind AI — Health Endpoint
GET /api/health

Returns service status. This endpoint does NOT require authentication
and does NOT require a database connection. It should always respond.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns the current health status of the DocuMind AI backend service.",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns basic service status without requiring authentication or database access.
    Used by load balancers, Docker health checks, and monitoring systems.
    """
    return HealthResponse(
        status="ok",
        service="documind-backend",
        version="1.0.0",
        environment=settings.app_env,
    )
