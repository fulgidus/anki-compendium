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
    Health check endpoint.
    Verifies database connectivity.
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
