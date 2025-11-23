"""
PDF upload endpoint for Anki flashcard generation.
"""
import json
import logging
from io import BytesIO
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_current_active_user
from app.core.validators import (
    generate_unique_filename,
    sanitize_filename,
    validate_file_size,
    validate_page_range,
    validate_pdf_file,
)
from app.database import get_db
from app.models.user import User
from app.schemas.job import CardDensity, JobCreate, JobResponse
from app.services.job_service import job_service
from app.services.storage_service import storage_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to process"),
    page_start: Optional[int] = Form(None, description="Starting page number (1-indexed)", ge=1),
    page_end: Optional[int] = Form(None, description="Ending page number (1-indexed)", ge=1),
    card_density: CardDensity = Form(CardDensity.MEDIUM, description="Card generation density"),
    subject: Optional[str] = Form(None, description="Subject/topic of the content", max_length=255),
    chapter: Optional[str] = Form(None, description="Chapter or section name", max_length=255),
    custom_tags: Optional[str] = Form(None, description="Custom tags as JSON array (e.g., [\"physics\", \"mechanics\"])"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload PDF file for Anki flashcard generation.
    
    **File Requirements:**
    - Must be PDF format (application/pdf)
    - Maximum size: Configured in MAX_UPLOAD_SIZE_MB (default 100MB)
    - Filename will be sanitized and made unique
    
    **Optional Parameters:**
    - page_start/page_end: Process specific page range
    - card_density: Controls flashcard generation density (low/medium/high)
    - subject/chapter: Organize generated cards
    - custom_tags: Additional tags for cards (JSON array string)
    
    **Rate Limiting:**
    - 10 uploads per hour per user
    
    **Quota:**
    - Free tier: 30 cards per month
    - Premium tier: 1000 cards per month
    
    **Returns:**
    - Job object with ID and status
    - Use job ID to poll for completion status
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/upload" \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -F "file=@document.pdf" \\
      -F "page_start=1" \\
      -F "page_end=10" \\
      -F "card_density=medium" \\
      -F "subject=Physics" \\
      -F "chapter=Chapter 1" \\
      -F 'custom_tags=["mechanics", "kinematics"]'
    ```
    """
    # Validate PDF file type
    validate_pdf_file(file, settings.MAX_UPLOAD_SIZE_MB)
    
    # Validate and get file size
    file_size = await validate_file_size(file, settings.MAX_UPLOAD_SIZE_MB)
    
    # Validate page range
    validate_page_range(page_start, page_end)
    
    # Check user quota
    if current_user.cards_generated_month >= current_user.cards_limit_month:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Monthly card limit reached ({current_user.cards_limit_month} cards). "
                   f"Upgrade your plan or wait for next month."
        )
    
    # Parse custom tags
    tags_list = None
    if custom_tags:
        try:
            tags_list = json.loads(custom_tags)
            if not isinstance(tags_list, list):
                raise ValueError("Tags must be a JSON array")
            if not all(isinstance(tag, str) for tag in tags_list):
                raise ValueError("All tags must be strings")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid custom_tags format: {str(e)}. Expected JSON array of strings."
            )
    
    # Validate filename exists
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    # Generate unique filename
    unique_filename = generate_unique_filename(str(current_user.id), file.filename)
    
    # Upload file to MinIO
    try:
        # Read file content
        file_content = await file.read()
        file_data = BytesIO(file_content)
        
        # Upload to storage
        object_path = await storage_service.upload_pdf(
            user_id=current_user.id,
            filename=unique_filename,
            file_data=file_data,
            file_size=file_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to storage: {str(e)}"
        )
    
    # Create job in database with all settings as separate fields
    try:
        job = await job_service.create_job(
            db=db,
            job_data=JobCreate(
                user_id=current_user.id,
                source_filename=file.filename,
                source_file_path=object_path,
                page_start=page_start,
                page_end=page_end,
                card_density=card_density.value,
                subject=subject,
                chapter=chapter,
                custom_tags=tags_list,
                settings=None  # Legacy field, keeping for backward compatibility
            )
        )
    except Exception as e:
        # Cleanup uploaded file on failure
        try:
            await storage_service.delete_file(
                bucket=settings.MINIO_BUCKET_PDFS,
                object_name=object_path
            )
        except:
            pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )
    
    # Trigger n8n workflow via webhook
    try:
        webhook_url = f"{settings.N8N_WEBHOOK_URL}/webhook/process-pdf"
        webhook_payload = {
            "job_id": str(job.id),
            "user_id": str(current_user.id),
            "source_filename": file.filename,
            "source_file_path": object_path,
            "page_start": page_start,
            "page_end": page_end,
            "card_density": card_density.value,
            "subject": subject,
            "chapter": chapter,
            "custom_tags": tags_list
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Secret": settings.N8N_WEBHOOK_SECRET
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=webhook_payload, headers=headers)
            response.raise_for_status()
            
        logger.info(f"Triggered n8n workflow for job {job.id}")
        
    except httpx.HTTPError as e:
        logger.error(f"Failed to trigger n8n workflow for job {job.id}: {e}")
        # Job will remain in PENDING status and can be retried manually or via admin interface
    except Exception as e:
        logger.error(f"Unexpected error triggering n8n workflow for job {job.id}: {e}")
    
    return JobResponse.model_validate(job)
