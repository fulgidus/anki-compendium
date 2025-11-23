"""
Dashboard API endpoints for statistics and activity feeds.
"""
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import ActivityItem, DashboardStats
from app.services.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/stats", response_model=DashboardStats, status_code=status.HTTP_200_OK)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics for the current user.
    
    Returns key metrics including:
    - Total number of decks created
    - Total number of flashcards across all decks
    - Number of active jobs (pending/processing)
    - Decks created in the last 7 days
    - Decks created in the last 30 days
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: Dashboard statistics object
    - 401: Unauthorized (invalid or missing token)
    - 500: Internal server error
    """
    try:
        logger.info(f"Fetching dashboard stats for user {current_user.id}")
        stats = await dashboard_service.get_stats(current_user.id, db)
        return stats
    
    except Exception as e:
        logger.error(f"Error fetching dashboard stats for user {current_user.id}: {str(e)}")
        raise


@router.get("/activity", response_model=List[ActivityItem], status_code=status.HTTP_200_OK)
async def get_recent_activity(
    limit: int = Query(5, ge=1, le=20, description="Maximum number of activity items to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent activity for the current user.
    
    Returns a combined, chronologically sorted list of recent jobs and decks.
    Activity items include both processing jobs and completed decks.
    
    **Query Parameters:**
    - limit: Maximum number of items to return (1-20, default: 5)
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: List of activity items sorted by timestamp (newest first)
    - 401: Unauthorized (invalid or missing token)
    - 500: Internal server error
    
    **Activity Item Types:**
    - `job`: PDF processing job with status and progress
    - `deck`: Generated Anki deck with card count
    """
    try:
        logger.info(f"Fetching recent activity for user {current_user.id} (limit={limit})")
        activity = await dashboard_service.get_activity(current_user.id, limit, db)
        return activity
    
    except Exception as e:
        logger.error(f"Error fetching activity for user {current_user.id}: {str(e)}")
        raise
