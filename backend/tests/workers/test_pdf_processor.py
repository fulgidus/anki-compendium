"""
Tests for Celery worker tasks.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.models.job import JobStatus
from app.workers.tasks import process_pdf_task, _process_pdf_async


class TestProcessPDFTask:
    """Tests for the process_pdf_task Celery task."""
    
    @pytest.fixture
    def mock_job(self):
        """Create a mock job."""
        job_id = uuid4()
        user_id = uuid4()
        
        job = MagicMock()
        job.id = job_id
        job.user_id = user_id
        job.source_filename = "test.pdf"
        job.source_file_path = f"{user_id}/test.pdf"
        job.status = JobStatus.PENDING
        job.progress_percent = 0
        job.page_start = 1
        job.page_end = 10
        job.card_density = "medium"
        job.subject = "Physics"
        job.chapter = "Chapter 1"
        job.custom_tags = ["physics", "mechanics"]
        job.settings = None  # Legacy field
        
        return job
    
    @pytest.fixture
    def mock_pipeline_result(self):
        """Create a mock RAG pipeline result."""
        return {
            "output_path": "/tmp/test.apkg",
            "num_pages": 10,
            "num_chunks": 20,
            "num_topics": 5,
            "num_tags": 8,
            "num_cards": 50,
        }
    
    @pytest.mark.asyncio
    async def test_process_pdf_success(self, mock_job, mock_pipeline_result):
        """Test successful PDF processing."""
        with patch('app.workers.tasks.job_service') as mock_job_service, \
             patch('app.workers.tasks.storage_service') as mock_storage_service, \
             patch('app.workers.tasks.generate_anki_deck_from_pdf') as mock_pipeline, \
             patch('app.workers.tasks.AsyncSessionLocal') as mock_session:
            
            # Setup mocks
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            mock_job_service.get_job = AsyncMock(return_value=mock_job)
            mock_storage_service.get_download_url = AsyncMock(return_value="http://minio/test.pdf")
            mock_pipeline.return_value = mock_pipeline_result
            mock_storage_service.upload_deck = AsyncMock(return_value="decks/test.apkg")
            
            # Mock httpx download
            with patch('httpx.AsyncClient') as mock_httpx:
                mock_response = MagicMock()
                mock_response.content = b"PDF content"
                mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                
                # Mock file operations
                with patch('builtins.open', create=True) as mock_open, \
                     patch('os.path.getsize', return_value=1024), \
                     patch('os.remove'):
                    
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Execute task
                    task = MagicMock()
                    result = await _process_pdf_async(task, mock_job.id)
                    
                    # Assertions
                    assert result['status'] == 'completed'
                    assert result['job_id'] == str(mock_job.id)
                    assert result['num_cards'] == 50
                    
                    # Verify pipeline was called
                    mock_pipeline.assert_called_once()
                    
                    # Verify deck was uploaded
                    mock_storage_service.upload_deck.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_pdf_job_not_found(self):
        """Test handling of non-existent job."""
        with patch('app.workers.tasks.job_service') as mock_job_service, \
             patch('app.workers.tasks.AsyncSessionLocal') as mock_session:
            
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            mock_job_service.get_job = AsyncMock(return_value=None)
            
            task = MagicMock()
            job_id = uuid4()
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="not found"):
                await _process_pdf_async(task, job_id)
    
    @pytest.mark.asyncio
    async def test_process_pdf_pipeline_failure(self, mock_job):
        """Test handling of RAG pipeline failure."""
        with patch('app.workers.tasks.job_service') as mock_job_service, \
             patch('app.workers.tasks.storage_service') as mock_storage_service, \
             patch('app.workers.tasks.generate_anki_deck_from_pdf') as mock_pipeline, \
             patch('app.workers.tasks.AsyncSessionLocal') as mock_session:
            
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db
            
            mock_job_service.get_job = AsyncMock(return_value=mock_job)
            mock_storage_service.get_download_url = AsyncMock(return_value="http://minio/test.pdf")
            mock_pipeline.side_effect = Exception("Pipeline failed")
            
            # Mock httpx download
            with patch('httpx.AsyncClient') as mock_httpx:
                mock_response = MagicMock()
                mock_response.content = b"PDF content"
                mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
                
                with patch('builtins.open', create=True), \
                     patch('os.remove'):
                    
                    task = MagicMock()
                    
                    # Should raise exception and update job to FAILED
                    with pytest.raises(Exception, match="Pipeline failed"):
                        await _process_pdf_async(task, mock_job.id)
                    
                    # Verify job was marked as failed
                    mock_job_service.fail_job.assert_called_once()


class TestTaskRetry:
    """Tests for task retry logic."""
    
    def test_retry_on_failure(self):
        """Test that task retries on failure."""
        with patch('app.workers.tasks.asyncio.run') as mock_asyncio:
            mock_asyncio.side_effect = Exception("Test error")
            
            task = process_pdf_task
            
            # Mock the task request
            with patch.object(task, 'request') as mock_request, \
                 patch.object(task, 'retry') as mock_retry:
                
                mock_request.retries = 0
                mock_retry.side_effect = Exception("Retry scheduled")
                
                # Should trigger retry
                with pytest.raises(Exception):
                    task.apply(args=["test-job-id"]).get()


class TestTaskConfiguration:
    """Tests for task configuration."""
    
    def test_task_registered(self):
        """Test that task is registered with Celery."""
        from app.celery_app import celery_app
        
        assert "app.workers.process_pdf" in celery_app.tasks
    
    def test_task_settings(self):
        """Test that task has correct settings."""
        assert process_pdf_task.max_retries == 3
        assert process_pdf_task.default_retry_delay == 300
