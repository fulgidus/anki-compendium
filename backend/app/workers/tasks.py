"""
Celery tasks for PDF processing and Anki deck generation.

This module contains the main worker tasks that process PDFs
and generate Anki decks asynchronously.
"""

import asyncio
import logging
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
from uuid import UUID

from celery import Task
from sqlalchemy import update

from app.celery_app import celery_app
from app.config import settings
from app.database import AsyncSessionLocal
from app.models.deck import Deck
from app.models.job import Job, JobStatus
from app.models.user import User
from app.rag.pipeline import generate_anki_deck_from_pdf
from app.services.job_service import job_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)


class ProcessPDFTask(Task):
    """
    Custom Celery task class for PDF processing with enhanced error handling.
    
    Provides lifecycle hooks for task failure and success.
    """
    
    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """
        Handle task failure.
        
        Updates the job status to FAILED and stores error information.
        
        Args:
            exc: Exception that caused the failure
            task_id: Unique task identifier
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception info object
        """
        logger.error(f"Task {task_id} failed: {exc}")
        logger.error(f"Exception info: {einfo}")
        
        # Extract job_id from args
        if args and len(args) > 0:
            job_id = args[0]
            
            # Update job status in database
            asyncio.run(self._mark_job_failed(job_id, str(exc), str(einfo)))
    
    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """
        Handle task success.
        
        Logs successful completion.
        
        Args:
            retval: Return value from the task
            task_id: Unique task identifier
            args: Task positional arguments
            kwargs: Task keyword arguments
        """
        logger.info(f"Task {task_id} completed successfully")
        logger.info(f"Result: {retval}")
    
    async def _mark_job_failed(self, job_id: str, error_message: str) -> None:
        """
        Mark job as failed in the database.
        
        Args:
            job_id: Job UUID
            error_message: Error message
        """
        try:
            async with AsyncSessionLocal() as db:
                await job_service.fail_job(
                    db=db,
                    job_id=UUID(job_id),
                    error_message=error_message
                )
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")


@celery_app.task(
    bind=True,
    base=ProcessPDFTask,
    name="app.workers.process_pdf",
    max_retries=3,
    default_retry_delay=300,  # 5 minutes between retries
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff
    retry_jitter=True,  # Add random jitter to retry delays
)
def process_pdf_task(self, job_id: str) -> Dict[str, Any]:
    """
    Process PDF and generate Anki deck.
    
    This is the main worker task that:
    1. Retrieves job details from database
    2. Downloads PDF from MinIO
    3. Runs the RAG pipeline to generate flashcards
    4. Uploads the resulting .apkg file to MinIO
    5. Creates a Deck record in the database
    6. Updates job status and user statistics
    
    Args:
        job_id: UUID of the job to process (as string)
    
    Returns:
        Dictionary containing processing results
    
    Raises:
        Exception: On processing errors (will trigger retry)
    """
    logger.info(f"Starting PDF processing for job {job_id}")
    
    try:
        # Run async processing
        result = asyncio.run(_process_pdf_async(self, UUID(job_id)))
        logger.info(f"Completed PDF processing for job {job_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        logger.error(traceback.format_exc())
        
        # Check if we should retry
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e)
        else:
            logger.error(f"Max retries reached for job {job_id}")
            raise


async def _process_pdf_async(task: Task, job_id: UUID) -> Dict[str, Any]:
    """
    Async implementation of PDF processing workflow.
    
    This function orchestrates the entire pipeline:
    - Database operations
    - File downloads and uploads
    - RAG pipeline execution
    - Status updates and error handling
    
    Args:
        task: Celery task instance (for progress updates and retries)
        job_id: UUID of the job to process
    
    Returns:
        Dictionary with processing results
    
    Raises:
        ValueError: If job not found or data invalid
        Exception: On processing errors
    """
    pdf_local_path = None
    output_local_path = None
    
    try:
        async with AsyncSessionLocal() as db:
            # Step 1: Retrieve job from database
            logger.info(f"Retrieving job {job_id}")
            job = await job_service.get_job(db, job_id)
            
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            logger.info(f"Processing job: {job.source_filename}")
            
            # Step 2: Update status to PROCESSING
            logger.info("Updating job status to PROCESSING")
            job.status = JobStatus.PROCESSING
            job.progress_percent = 0
            await db.commit()
            await db.refresh(job)
            
            # Step 3: Download PDF from MinIO
            logger.info("Downloading PDF from MinIO")
            pdf_filename = Path(job.source_file_path).name
            pdf_local_path = f"/tmp/{job_id}_{pdf_filename}"
            
            # Download file
            presigned_url = await storage_service.get_download_url(
                bucket=settings.MINIO_BUCKET_PDFS,
                object_name=job.source_file_path
            )
            
            # Use httpx to download the file
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(presigned_url)
                response.raise_for_status()
                
                with open(pdf_local_path, 'wb') as f:
                    f.write(response.content)
            
            logger.info(f"PDF downloaded to {pdf_local_path}")
            
            # Update progress
            job.progress_percent = 10
            await db.commit()
            
            # Step 4: Prepare output path for .apkg file
            output_filename = f"{job_id}.apkg"
            output_local_path = f"/tmp/{output_filename}"
            
            # Step 5: Extract settings from job
            # Use direct fields from job model (not settings dict)
            subject = job.subject or ""
            chapter = job.chapter or ""
            card_density = job.card_density or "medium"
            custom_tags = job.custom_tags or []
            page_start = job.page_start
            page_end = job.page_end
            
            # Determine deck name
            deck_name = chapter or subject or Path(job.source_filename).stem
            
            # Step 6: Validate API key before running pipeline
            if not settings.GEMINI_API_KEY:
                raise ValueError(
                    "GEMINI_API_KEY not configured. "
                    "Please set your Google Gemini API key in the .env file. "
                    "Get your key from: https://makersuite.google.com/app/apikey"
                )
            
            # Step 7: Run RAG pipeline
            logger.info("Running RAG pipeline")
            
            job.progress_percent = 20
            await db.commit()
            
            pipeline_result = await generate_anki_deck_from_pdf(
                pdf_path=pdf_local_path,
                output_path=output_local_path,
                gemini_api_key=settings.GEMINI_API_KEY,
                database_url=settings.DATABASE_URL,
                deck_name=deck_name,
                subject=subject,
                chapter=chapter,
                card_density=card_density,
                custom_tags=custom_tags,
                page_start=page_start,
                page_end=page_end,
            )
            
            logger.info(f"RAG pipeline completed: {pipeline_result.get('num_cards', 0)} cards generated")
            
            # Update progress
            job.progress_percent = 80
            await db.commit()
            
            # Step 8: Upload .apkg file to MinIO
            logger.info("Uploading .apkg to MinIO")
            
            # Read the generated file
            with open(output_local_path, 'rb') as f:
                deck_file_data = f.read()
            
            # Upload to storage
            deck_object_path = await storage_service.upload_deck(
                user_id=job.user_id,
                deck_id=job_id,  # Use job_id as temp identifier
                filename=output_filename,
                file_data=deck_file_data
            )
            
            logger.info(f"Deck uploaded to {deck_object_path}")
            
            # Get file size
            deck_file_size = os.path.getsize(output_local_path)
            
            # Update progress
            job.progress_percent = 90
            await db.commit()
            
            # Step 9: Create Deck record in database
            logger.info("Creating Deck record")
            
            deck = Deck(
                user_id=job.user_id,
                job_id=job.id,
                name=deck_name,
                description=f"Generated from {job.source_filename}",
                source_filename=job.source_filename,
                card_count=pipeline_result.get("num_cards", 0),
                file_path=deck_object_path,
                file_size_bytes=deck_file_size,
                tags=custom_tags or [],
                settings=job.settings,  # Use job.settings directly
            )
            
            db.add(deck)
            await db.flush()  # Get the deck ID
            
            logger.info(f"Deck created with ID: {deck.id}")
            
            # Step 10: Update job to COMPLETED
            logger.info("Updating job status to COMPLETED")
            
            job.status = JobStatus.COMPLETED
            job.progress_percent = 100
            job.result_deck_id = deck.id
            job.completed_at = datetime.utcnow()
            
            await db.commit()
            
            # Step 11: Update user card count
            logger.info("Updating user card count")
            
            num_cards = pipeline_result.get("num_cards", 0)
            
            await db.execute(
                update(User)
                .where(User.id == job.user_id)
                .values(cards_generated_month=User.cards_generated_month + num_cards)
            )
            
            await db.commit()
            
            logger.info(f"User card count updated (+{num_cards} cards)")
            
            # Step 12: Cleanup temporary files
            _cleanup_temp_files(pdf_local_path, output_local_path)
            
            # Return success result
            return {
                "status": "completed",
                "job_id": str(job_id),
                "deck_id": str(deck.id),
                "num_cards": num_cards,
                "num_pages": pipeline_result.get("num_pages", 0),
                "num_chunks": pipeline_result.get("num_chunks", 0),
                "num_topics": pipeline_result.get("num_topics", 0),
                "num_tags": pipeline_result.get("num_tags", 0),
            }
            
    except Exception as e:
        logger.error(f"Error in PDF processing: {e}")
        logger.error(traceback.format_exc())
        
        # Cleanup temp files on error
        _cleanup_temp_files(pdf_local_path, output_local_path)
        
        # Update job status to FAILED
        try:
            async with AsyncSessionLocal() as db:
                await job_service.fail_job(
                    db=db,
                    job_id=job_id,
                    error_message=f"{str(e)}\n\nStack trace:\n{traceback.format_exc()}"
                )
        except Exception as db_error:
            logger.error(f"Failed to update job status: {db_error}")
        
        # Re-raise to trigger Celery retry
        raise


def _cleanup_temp_files(*file_paths: str) -> None:
    """
    Clean up temporary files.
    
    Args:
        *file_paths: Variable number of file paths to delete
    """
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
