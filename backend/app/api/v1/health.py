"""
Health check and system info endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas.health import HealthResponse, InfoResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint (liveness probe).
    Verifies database connectivity.
    
    Use this for Kubernetes liveness probes or basic health checks.
    For readiness checks, use /ready endpoint.
    """
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "unhealthy",
        database=db_status,
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint (readiness probe).
    Verifies that the application is ready to accept traffic.
    
    Checks:
    - Database connectivity
    - Database can execute queries
    
    Use this for Kubernetes readiness probes or load balancer health checks.
    """
    try:
        # Verify database is ready to accept queries
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        _ = result.scalar()
        db_status = "ready"
    except Exception as e:
        db_status = f"not ready: {str(e)}"

    return HealthResponse(
        status="ready" if db_status == "ready" else "not ready",
        database=db_status,
    )


@router.get("/info", response_model=InfoResponse)
async def info():
    """
    System information endpoint.
    Returns application metadata.
    """
    return InfoResponse(
        name=settings.PROJECT_NAME,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
    )
