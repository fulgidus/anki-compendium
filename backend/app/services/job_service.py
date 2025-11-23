"""
Job service for PDF processing job management.

Handles job creation, status updates, and queue management.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
import math

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    """
    Job service for managing PDF processing jobs.
    
    Handles job lifecycle from creation to completion.
    """

    async def create_job(self, db: AsyncSession, job_data: JobCreate) -> Job:
        """
        Create a new processing job.
        
        Args:
            db: Database session
            job_data: Job creation data
            
        Returns:
            Created job instance
        """
        job = Job(
            user_id=job_data.user_id,
            source_filename=job_data.source_filename,
            source_file_path=job_data.source_file_path,
            page_start=job_data.page_start,
            page_end=job_data.page_end,
            card_density=job_data.card_density,
            subject=job_data.subject,
            chapter=job_data.chapter,
            custom_tags=job_data.custom_tags,
            settings=job_data.settings,
            status=JobStatus.PENDING,
            progress_percent=0,
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)

        return job

    async def get_job(self, db: AsyncSession, job_id: UUID) -> Optional[Job]:
        """
        Get job by ID.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            Job instance or None
        """
        result = await db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()

    async def get_user_jobs(
        self,
        db: AsyncSession,
        user_id: UUID,
        status: Optional[JobStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[Job], int]:
        """
        Get paginated jobs for user with optional status filter.
        
        Args:
            db: Database session
            user_id: User ID
            status: Optional job status filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (jobs list, total count)
        """
        # Build base query
        query = select(Job).where(Job.user_id == user_id)
        
        # Apply status filter if provided
        if status is not None:
            query = query.where(Job.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination and ordering
        query = query.order_by(Job.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        jobs = list(result.scalars().all())
        
        return jobs, total

    async def update_job(
        self, db: AsyncSession, job_id: UUID, job_update: JobUpdate
    ) -> Optional[Job]:
        """
        Update job status and progress.
        
        Args:
            db: Database session
            job_id: Job ID
            job_update: Job update data
            
        Returns:
            Updated job instance or None
        """
        job = await self.get_job(db, job_id)
        if not job:
            return None

        update_data = job_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        await db.commit()
        await db.refresh(job)

        return job

    async def start_job(self, db: AsyncSession, job_id: UUID) -> Optional[Job]:
        """
        Mark job as processing.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            Updated job instance or None
        """
        return await self.update_job(
            db,
            job_id,
            JobUpdate(status=JobStatus.PROCESSING.value),
        )

    async def complete_job(
        self, db: AsyncSession, job_id: UUID, result_deck_id: UUID
    ) -> Optional[Job]:
        """
        Mark job as completed.
        
        Args:
            db: Database session
            job_id: Job ID
            result_deck_id: ID of generated deck
            
        Returns:
            Updated job instance or None
        """
        return await self.update_job(
            db,
            job_id,
            JobUpdate(
                status=JobStatus.COMPLETED.value,
                progress_percent=100,
                result_deck_id=result_deck_id,
                completed_at=datetime.utcnow(),
            ),
        )

    async def fail_job(
        self, db: AsyncSession, job_id: UUID, error_message: str
    ) -> Optional[Job]:
        """
        Mark job as failed.
        
        Args:
            db: Database session
            job_id: Job ID
            error_message: Error message
            
        Returns:
            Updated job instance or None
        """
        return await self.update_job(
            db,
            job_id,
            JobUpdate(
                status=JobStatus.FAILED.value,
                error_message=error_message,
                completed_at=datetime.utcnow(),
            ),
        )

    async def cancel_job(self, db: AsyncSession, job_id: UUID) -> Optional[Job]:
        """
        Cancel a pending or processing job.
        
        Args:
            db: Database session
            job_id: Job ID
            
        Returns:
            Updated job instance or None
        """
        return await self.update_job(
            db,
            job_id,
            JobUpdate(
                status=JobStatus.CANCELLED.value,
                completed_at=datetime.utcnow(),
            ),
        )

    async def retry_job(
        self,
        db: AsyncSession,
        job_id: UUID,
        user_id: UUID
    ) -> Job:
        """
        Retry a failed job.
        
        Verifies ownership and that job is in FAILED status,
        then resets it to PENDING for reprocessing.
        
        Args:
            db: Database session
            job_id: Job ID
            user_id: User ID for ownership verification
            
        Returns:
            Updated job instance
            
        Raises:
            HTTPException: If job not found, not owned by user, or not in FAILED status
        """
        # Get job
        job = await self.get_job(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify ownership
        if job.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to retry this job"
            )
        
        # Check if job is in FAILED status
        if job.status != JobStatus.FAILED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only retry jobs with FAILED status. Current status: {job.status.value}"
            )
        
        # Check retry limit
        if job.retry_count >= job.max_retries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum retry limit ({job.max_retries}) reached"
            )
        
        # Reset job status
        job.status = JobStatus.PENDING
        job.progress_percent = 0
        job.error_message = None
        job.retry_count += 1
        job.completed_at = None
        
        await db.commit()
        await db.refresh(job)
        
        # TODO: Requeue job in Celery/RabbitMQ when integration is ready
        
        return job

    async def delete_job(
        self,
        db: AsyncSession,
        job_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete or cancel a job.
        
        If job is PENDING or PROCESSING, it will be cancelled.
        Otherwise, it will be deleted from the database.
        
        Args:
            db: Database session
            job_id: Job ID
            user_id: User ID for ownership verification
            
        Raises:
            HTTPException: If job not found or not owned by user
        """
        # Get job
        job = await self.get_job(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify ownership
        if job.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this job"
            )
        
        # If job is active, cancel it
        if job.status in [JobStatus.PENDING, JobStatus.PROCESSING]:
            await self.cancel_job(db, job_id)
        else:
            # Delete job
            await db.delete(job)
            await db.commit()


# Singleton instance
job_service = JobService()
