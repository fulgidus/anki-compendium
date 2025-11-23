"""
Dashboard service for statistics and activity aggregation.
"""
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.deck import Deck
from app.models.job import Job, JobStatus
from app.schemas.dashboard import ActivityItem, DashboardStats


class DashboardService:
    """Service for dashboard operations."""
    
    @staticmethod
    async def get_stats(user_id: UUID, db: AsyncSession) -> DashboardStats:
        """
        Calculate dashboard statistics for a user.
        
        Args:
            user_id: UUID of the user
            db: Database session
            
        Returns:
            DashboardStats object with calculated statistics
        """
        try:
            # Calculate total decks
            total_decks_result = await db.execute(
                select(func.count(Deck.id)).where(Deck.user_id == user_id)
            )
            total_decks = total_decks_result.scalar() or 0
            
            # Calculate total cards (sum of card_count from all decks)
            total_cards_result = await db.execute(
                select(func.sum(Deck.card_count)).where(Deck.user_id == user_id)
            )
            total_cards = total_cards_result.scalar() or 0
            
            # Calculate active jobs (pending or processing)
            active_jobs_result = await db.execute(
                select(func.count(Job.id)).where(
                    and_(
                        Job.user_id == user_id,
                        or_(
                            Job.status == JobStatus.PENDING,
                            Job.status == JobStatus.PROCESSING
                        )
                    )
                )
            )
            active_jobs = active_jobs_result.scalar() or 0
            
            # Calculate decks created in the last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            decks_week_result = await db.execute(
                select(func.count(Deck.id)).where(
                    and_(
                        Deck.user_id == user_id,
                        Deck.created_at >= week_ago
                    )
                )
            )
            decks_this_week = decks_week_result.scalar() or 0
            
            # Calculate decks created in the last 30 days
            month_ago = datetime.utcnow() - timedelta(days=30)
            decks_month_result = await db.execute(
                select(func.count(Deck.id)).where(
                    and_(
                        Deck.user_id == user_id,
                        Deck.created_at >= month_ago
                    )
                )
            )
            decks_this_month = decks_month_result.scalar() or 0
            
            return DashboardStats(
                total_decks=total_decks,
                total_cards=total_cards,
                active_jobs=active_jobs,
                decks_this_week=decks_this_week,
                decks_this_month=decks_this_month
            )
        
        except Exception as e:
            logger.error(f"Error calculating dashboard stats for user {user_id}: {str(e)}")
            raise
    
    @staticmethod
    async def get_activity(
        user_id: UUID,
        limit: int,
        db: AsyncSession
    ) -> List[ActivityItem]:
        """
        Get recent activity (jobs and decks) for a user.
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of items to return
            db: Database session
            
        Returns:
            List of ActivityItem objects sorted by timestamp descending
        """
        try:
            # Fetch recent jobs
            jobs_result = await db.execute(
                select(Job)
                .where(Job.user_id == user_id)
                .order_by(Job.created_at.desc())
                .limit(limit)
            )
            jobs = jobs_result.scalars().all()
            
            # Fetch recent decks
            decks_result = await db.execute(
                select(Deck)
                .where(Deck.user_id == user_id)
                .order_by(Deck.created_at.desc())
                .limit(limit)
            )
            decks = decks_result.scalars().all()
            
            # Convert to ActivityItem objects
            activity_items: List[ActivityItem] = []
            
            # Add jobs to activity
            for job in jobs:
                activity_items.append(ActivityItem(
                    id=job.id,
                    type='job',
                    title=f"Processing: {job.source_filename}",
                    timestamp=job.created_at,
                    status=job.status.value,
                    metadata={
                        'progress': job.progress_percent,
                        'card_density': job.card_density,
                        'subject': job.subject,
                        'chapter': job.chapter
                    }
                ))
            
            # Add decks to activity
            for deck in decks:
                activity_items.append(ActivityItem(
                    id=deck.id,
                    type='deck',
                    title=deck.name,
                    timestamp=deck.created_at,
                    status=None,
                    metadata={
                        'card_count': deck.card_count,
                        'source_filename': deck.source_filename,
                        'language': deck.language
                    }
                ))
            
            # Sort by timestamp descending and limit
            activity_items.sort(key=lambda x: x.timestamp, reverse=True)
            return activity_items[:limit]
        
        except Exception as e:
            logger.error(f"Error fetching activity for user {user_id}: {str(e)}")
            raise


# Singleton instance
dashboard_service = DashboardService()
