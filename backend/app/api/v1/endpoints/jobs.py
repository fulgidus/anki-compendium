"""
Job management endpoints for tracking and controlling PDF processing jobs.
"""
import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.database import get_db
from app.models.job import JobStatus
from app.models.user import User
from app.schemas.job import JobListResponse, JobResponse, JobStatusResponse
from app.services.job_service import job_service

router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    status_filter: Optional[JobStatus] = Query(None, description="Filter by job status"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all jobs for the current user with pagination and optional filtering.
    
    **Query Parameters:**
    - status: Filter by job status (pending, processing, completed, failed, cancelled)
    - page: Page number (1-indexed, default=1)
    - page_size: Items per page (default=20, max=100)
    
    **Returns:**
    - Paginated list of jobs with metadata
    - Total count and page information
    
    **Example:**
    ```bash
    # Get all jobs, page 1
    GET /api/v1/jobs?page=1&page_size=20
    
    # Get only failed jobs
    GET /api/v1/jobs?status=failed
    
    # Get completed jobs, page 2
    GET /api/v1/jobs?status=completed&page=2
    ```
    """
    # Get jobs from service
    jobs, total = await job_service.get_user_jobs(
        db=db,
        user_id=current_user.id,
        status=status_filter,
        page=page,
        page_size=page_size
    )
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=total_pages,
        items=[JobResponse.model_validate(job) for job in jobs]
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific job.
    
    **Path Parameters:**
    - job_id: UUID of the job
    
    **Returns:**
    - Complete job details including status, progress, and errors
    
    **Errors:**
    - 404: Job not found
    - 403: Not authorized to access this job
    
    **Example:**
    ```bash
    GET /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    # Get job
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    
    return JobResponse.model_validate(job)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get simplified job status for polling.
    
    This endpoint returns only essential status information,
    optimized for frequent polling from frontend applications.
    
    **Path Parameters:**
    - job_id: UUID of the job
    
    **Returns:**
    - Job ID, status, progress, and result deck ID (if completed)
    
    **Errors:**
    - 404: Job not found
    - 403: Not authorized to access this job
    
    **Example:**
    ```bash
    # Poll every 2 seconds until completed
    GET /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/status
    ```
    """
    # Get job
    job = await job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify ownership
    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this job"
        )
    
    return JobStatusResponse(
        id=job.id,
        status=job.status.value,
        progress_percent=job.progress_percent,
        error_message=job.error_message,
        result_deck_id=job.result_deck_id
    )


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a failed job.
    
    Resets a failed job to PENDING status for reprocessing.
    Only works for jobs in FAILED status and within retry limits.
    
    **Path Parameters:**
    - job_id: UUID of the job to retry
    
    **Returns:**
    - Updated job with PENDING status
    
    **Errors:**
    - 404: Job not found
    - 403: Not authorized to retry this job
    - 400: Job is not in FAILED status or retry limit exceeded
    
    **Example:**
    ```bash
    POST /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000/retry
    ```
    """
    job = await job_service.retry_job(
        db=db,
        job_id=job_id,
        user_id=current_user.id
    )
    
    return JobResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete or cancel a job.
    
    - If job is PENDING or PROCESSING: Cancels the job
    - If job is COMPLETED, FAILED, or CANCELLED: Deletes the job record
    
    **Path Parameters:**
    - job_id: UUID of the job to delete
    
    **Returns:**
    - 204 No Content on success
    
    **Errors:**
    - 404: Job not found
    - 403: Not authorized to delete this job
    
    **Example:**
    ```bash
    DELETE /api/v1/jobs/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    await job_service.delete_job(
        db=db,
        job_id=job_id,
        user_id=current_user.id
    )
    
    return None
