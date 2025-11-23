"""
End-to-End Tests for PDF Upload Endpoint.

Comprehensive white-box testing covering:
- Authentication flow
- File validation
- Job creation
- MinIO storage
- Celery task queuing
- Database state verification
"""
import io
import json
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


# ============================================================================
# Test Helpers
# ============================================================================

def create_test_pdf(size_bytes: int = 1024) -> io.BytesIO:
    """
    Create a minimal valid PDF file for testing.
    
    Args:
        size_bytes: Approximate size of PDF (minimum ~100 bytes for valid PDF)
    
    Returns:
        BytesIO object containing PDF data
    """
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
0000000293 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
380
%%EOF
"""
    
    # Pad to requested size if needed
    if len(pdf_content) < size_bytes:
        padding = b' ' * (size_bytes - len(pdf_content) - 10)
        # Insert padding before %%EOF
        pdf_content = pdf_content.replace(b'%%EOF', padding + b'\n%%EOF')
    
    return io.BytesIO(pdf_content)


def create_invalid_file(content: bytes = b"Not a PDF") -> io.BytesIO:
    """Create an invalid (non-PDF) file."""
    return io.BytesIO(content)


async def get_job_from_db(db: AsyncSession, job_id: str):
    """Helper to fetch job from database."""
    from app.models.job import Job
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def count_user_jobs(db: AsyncSession, user_id: UUID) -> int:
    """Helper to count jobs for a user."""
    from app.models.job import Job
    result = await db.execute(
        select(func.count()).select_from(Job).where(Job.user_id == user_id)
    )
    return result.scalar_one()


# ============================================================================
# Test: Authentication Flow
# ============================================================================

class TestAuthenticationFlow:
    """Test authentication requirements for upload endpoint."""
    
    @pytest.mark.anyio
    async def test_upload_requires_authentication(self, client: AsyncClient):
        """Test that upload endpoint rejects unauthenticated requests."""
        pdf_file = create_test_pdf()
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file, "application/pdf")}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    @pytest.mark.anyio
    async def test_upload_with_invalid_token(self, client: AsyncClient):
        """Test upload with invalid JWT token."""
        pdf_file = create_test_pdf()
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": "Bearer invalid_token_12345"}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    @pytest.mark.anyio
    async def test_upload_with_malformed_auth_header(self, client: AsyncClient):
        """Test upload with malformed Authorization header."""
        pdf_file = create_test_pdf()
        
        # Missing "Bearer" prefix
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            headers={"Authorization": "some_token"}
        )
        
        assert response.status_code == 401


# ============================================================================
# Test: File Validation
# ============================================================================

class TestFileValidation:
    """Test file type and size validation."""
    
    @pytest.mark.anyio
    async def test_upload_valid_pdf(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test successful upload of valid PDF file."""
        pdf_file = create_test_pdf(size_bytes=2048)
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            # Mock MinIO upload
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            
            # Mock Celery task
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Verify response structure
            assert "id" in data
            assert data["status"] == "pending"
            assert data["progress_percent"] == 0
            assert data["source_filename"] == "test.pdf"
            assert data["user_id"] == str(test_user.id)
            
            # Verify MinIO upload was called
            mock_upload.assert_called_once()
            
            # Verify Celery task was queued
            mock_task.assert_called_once()
    
    @pytest.mark.anyio
    async def test_upload_non_pdf_file(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test rejection of non-PDF file."""
        txt_file = create_invalid_file(b"This is a text file")
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("document.txt", txt_file, "text/plain")},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    @pytest.mark.anyio
    async def test_upload_file_without_pdf_extension(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test rejection of file without .pdf extension."""
        pdf_content = create_test_pdf()
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("document.txt", pdf_content, "application/pdf")},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "must have .pdf extension" in response.json()["detail"]
    
    @pytest.mark.anyio
    async def test_upload_empty_file(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test rejection of empty file."""
        empty_file = io.BytesIO(b"")
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("empty.pdf", empty_file, "application/pdf")},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    @pytest.mark.anyio
    async def test_upload_file_exceeds_size_limit(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test rejection of file exceeding size limit."""
        # Create file larger than MAX_UPLOAD_SIZE_MB
        large_size = (settings.MAX_UPLOAD_SIZE_MB + 1) * 1024 * 1024
        large_file = create_test_pdf(size_bytes=large_size)
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("large.pdf", large_file, "application/pdf")},
            headers=auth_headers
        )
        
        assert response.status_code == 413
        assert "exceeds maximum" in response.json()["detail"]
    
    @pytest.mark.anyio
    async def test_upload_missing_file_parameter(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test request with missing file parameter."""
        response = await client.post(
            "/api/v1/upload",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # FastAPI validation error


# ============================================================================
# Test: Job Creation & Database
# ============================================================================

class TestJobCreation:
    """Test job creation and database operations."""
    
    @pytest.mark.anyio
    async def test_job_created_in_database(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test that job is created in database with correct fields."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("document.pdf", pdf_file, "application/pdf")},
                data={
                    "card_density": "high",
                    "subject": "Physics",
                    "chapter": "Mechanics",
                    "page_start": "1",
                    "page_end": "10",
                    "custom_tags": '["physics", "mechanics"]'
                },
                headers=auth_headers
            )
            
            assert response.status_code == 201
            job_id = response.json()["id"]
            
            # Verify job in database
            job = await get_job_from_db(test_db, job_id)
            assert job is not None
            
            # Check all fields
            assert job is not None and job.user_id == test_user.id
            assert job is not None and job.source_filename == "document.pdf"
            assert job is not None and job.source_file_path == f"{test_user.id}/test.pdf"
            from app.models.job import JobStatus
            assert job is not None and job.status == JobStatus.PENDING
            assert job is not None and job.progress_percent == 0
            assert job is not None and job.card_density == "high"
            assert job is not None and job.subject == "Physics"
            assert job is not None and job.chapter == "Mechanics"
            assert job is not None and job.page_start == 1
            assert job is not None and job.page_end == 10
            assert job is not None and job.custom_tags == ["physics", "mechanics"]
            assert job is not None and job.retry_count == 0
            assert job is not None and job.max_retries == 3
            assert job.created_at is not None
            assert job.updated_at is not None
            assert job.completed_at is None
            assert job.result_deck_id is None
            assert job.error_message is None
    
    @pytest.mark.anyio
    async def test_job_with_default_settings(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test job creation with default settings (minimal parameters)."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 201
            job_id = response.json()["id"]
            
            # Verify defaults in database
            job = await get_job_from_db(test_db, job_id)
            assert job is not None and job.card_density == "medium"  # Default
            assert job.page_start is None
            assert job.page_end is None
            assert job.subject is None
            assert job.chapter is None
            assert job.custom_tags is None
    
    @pytest.mark.anyio
    async def test_page_range_validation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation of page range parameters."""
        pdf_file = create_test_pdf()
        
        # Test page_start > page_end
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            data={"page_start": "10", "page_end": "5"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "page_start cannot be greater than page_end" in response.json()["detail"]
        
        # Test page_start < 1
        pdf_file2 = create_test_pdf()
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file2, "application/pdf")},
            data={"page_start": "0"},
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Pydantic validation
    
    @pytest.mark.anyio
    async def test_custom_tags_validation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation of custom tags JSON format."""
        pdf_file = create_test_pdf()
        
        # Invalid JSON
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            data={"custom_tags": "not-valid-json"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid custom_tags format" in response.json()["detail"]
        
        # Valid JSON but not array
        pdf_file2 = create_test_pdf()
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file2, "application/pdf")},
            data={"custom_tags": '{"tag": "value"}'},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "must be a JSON array" in response.json()["detail"]


# ============================================================================
# Test: MinIO Storage Integration
# ============================================================================

class TestMinIOStorage:
    """Test MinIO storage integration."""
    
    @pytest.mark.anyio
    async def test_pdf_uploaded_to_minio(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test that PDF is uploaded to MinIO with correct path."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            expected_path = f"{test_user.id}/20250123_abc123_test.pdf"
            mock_upload.return_value = expected_path
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 201
            
            # Verify upload was called with correct parameters
            mock_upload.assert_called_once()
            call_args = mock_upload.call_args
            
            assert call_args.kwargs["user_id"] == test_user.id
            assert call_args.kwargs["filename"].endswith("_test.pdf")
            assert call_args.kwargs["file_size"] > 0
    
    @pytest.mark.anyio
    async def test_minio_failure_cleanup(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_db: AsyncSession
    ):
        """Test that job is not created if MinIO upload fails."""
        pdf_file = create_test_pdf()
        
        initial_count = await count_user_jobs(test_db, test_user.id)
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload:
            # Simulate MinIO failure
            mock_upload.side_effect = Exception("MinIO connection failed")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 500
            assert "Failed to upload file to storage" in response.json()["detail"]
            
            # Verify no job was created
            final_count = await count_user_jobs(test_db, test_user.id)
            assert final_count == initial_count


# ============================================================================
# Test: Celery Task Queuing
# ============================================================================

class TestCeleryTaskQueuing:
    """Test Celery task queuing integration."""
    
    @pytest.mark.anyio
    async def test_celery_task_queued(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test that Celery task is queued for processing."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            
            mock_celery_task = MagicMock()
            mock_celery_task.id = "celery-task-abc123"
            mock_task.return_value = mock_celery_task
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 201
            job_id = response.json()["id"]
            
            # Verify task was queued
            mock_task.assert_called_once_with(job_id)
    
    @pytest.mark.anyio
    async def test_job_created_even_if_celery_fails(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test that job is still created if Celery queuing fails."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            
            # Simulate Celery failure
            mock_task.side_effect = Exception("RabbitMQ connection failed")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            # Job should still be created
            assert response.status_code == 201
            job_id = response.json()["id"]
            
            # Verify job exists in database with PENDING status
            job = await get_job_from_db(test_db, job_id)
            assert job is not None
            from app.models.job import JobStatus
            assert job is not None and job.status == JobStatus.PENDING


# ============================================================================
# Test: User Quota Management
# ============================================================================

class TestUserQuota:
    """Test user quota enforcement."""
    
    @pytest.mark.anyio
    async def test_upload_blocked_when_quota_exceeded(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test that upload is blocked when monthly card limit is reached."""
        # Set user at quota limit
        test_user.cards_generated_month = test_user.cards_limit_month
        test_db.add(test_user)
        await test_db.commit()
        
        pdf_file = create_test_pdf()
        
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.pdf", pdf_file, "application/pdf")},
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Monthly card limit reached" in response.json()["detail"]
    
    @pytest.mark.anyio
    async def test_upload_allowed_when_under_quota(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test that upload is allowed when under quota."""
        # Ensure user is under quota
        test_user.cards_generated_month = 0
        test_db.add(test_user)
        await test_db.commit()
        
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 201


# ============================================================================
# Test: API Response Validation
# ============================================================================

class TestAPIResponse:
    """Test API response structure and content."""
    
    @pytest.mark.anyio
    async def test_response_structure(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test that response matches JobResponse schema."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                data={
                    "card_density": "medium",
                    "subject": "Math",
                    "chapter": "Algebra"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            
            # Required fields
            assert "id" in data
            assert "user_id" in data
            assert "status" in data
            assert "progress_percent" in data
            assert "source_filename" in data
            assert "source_file_path" in data
            assert "card_density" in data
            assert "retry_count" in data
            assert "max_retries" in data
            assert "created_at" in data
            assert "updated_at" in data
            
            # Optional fields
            assert "page_start" in data
            assert "page_end" in data
            assert "subject" in data
            assert "chapter" in data
            assert "custom_tags" in data
            assert "result_deck_id" in data
            assert "error_message" in data
            assert "completed_at" in data
            
            # Check types
            assert isinstance(data["id"], str)
            assert isinstance(data["status"], str)
            assert isinstance(data["progress_percent"], int)
            assert data["progress_percent"] == 0
            assert data["status"] == "pending"
    
    @pytest.mark.anyio
    async def test_response_includes_all_form_data(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test that response includes all submitted form data."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("physics_book.pdf", pdf_file, "application/pdf")},
                data={
                    "page_start": "5",
                    "page_end": "15",
                    "card_density": "high",
                    "subject": "Physics",
                    "chapter": "Thermodynamics",
                    "custom_tags": '["thermodynamics", "heat", "energy"]'
                },
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            
            assert data["page_start"] == 5
            assert data["page_end"] == 15
            assert data["card_density"] == "high"
            assert data["subject"] == "Physics"
            assert data["chapter"] == "Thermodynamics"
            assert data["custom_tags"] == ["thermodynamics", "heat", "energy"]


# ============================================================================
# Test: Error Handling & Edge Cases
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.anyio
    async def test_database_error_cleanup(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user
    ):
        """Test that MinIO file is cleaned up if database operation fails."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.services.storage_service.storage_service.delete_file") as mock_delete, \
             patch("app.services.job_service.job_service.create_job") as mock_create_job:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            
            # Simulate database failure
            mock_create_job.side_effect = Exception("Database connection lost")
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 500
            assert "Failed to create job" in response.json()["detail"]
            
            # Verify cleanup was attempted
            mock_delete.assert_called_once()
    
    @pytest.mark.anyio
    async def test_filename_sanitization(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user,
        test_db: AsyncSession
    ):
        """Test that filenames with special characters are sanitized."""
        pdf_file = create_test_pdf()
        
        with patch("app.services.storage_service.storage_service.upload_pdf") as mock_upload, \
             patch("app.workers.tasks.process_pdf_task.delay") as mock_task:
            
            mock_upload.return_value = f"{test_user.id}/test.pdf"
            mock_task.return_value = MagicMock(id="mock-task-id")
            
            # Filename with special characters
            dangerous_filename = "../../../etc/passwd.pdf"
            
            response = await client.post(
                "/api/v1/upload",
                files={"file": (dangerous_filename, pdf_file, "application/pdf")},
                headers=auth_headers
            )
            
            assert response.status_code == 201
            job_id = response.json()["id"]
            
            # Verify filename was sanitized in database
            job = await get_job_from_db(test_db, job_id)
            assert job is not None and job.source_filename == dangerous_filename  # Original preserved
            
            # But storage path should be sanitized
            call_args = mock_upload.call_args
            stored_filename = call_args.kwargs["filename"]
            assert "../" not in stored_filename
            assert "etc" not in stored_filename


# ============================================================================
# Summary Report Generator
# ============================================================================

def test_suite_summary():
    """
    Test Suite Summary
    
    This test suite covers the following scenarios:
    
    1. Authentication Flow (3 tests)
       - Unauthenticated requests rejected
       - Invalid token rejected
       - Malformed auth header rejected
    
    2. File Validation (6 tests)
       - Valid PDF accepted
       - Non-PDF files rejected
       - Files without .pdf extension rejected
       - Empty files rejected
       - Oversized files rejected
       - Missing file parameter rejected
    
    3. Job Creation & Database (4 tests)
       - Job created with all fields
       - Job created with defaults
       - Page range validation
       - Custom tags validation
    
    4. MinIO Storage (2 tests)
       - PDF uploaded to correct path
       - Cleanup on MinIO failure
    
    5. Celery Task Queuing (2 tests)
       - Task queued successfully
       - Job created even if queuing fails
    
    6. User Quota (2 tests)
       - Upload blocked at quota limit
       - Upload allowed under quota
    
    7. API Response (2 tests)
       - Response structure validation
       - All form data included in response
    
    8. Error Handling (2 tests)
       - Cleanup on database error
       - Filename sanitization
    
    Total: 23 comprehensive test scenarios
    """
    pass
