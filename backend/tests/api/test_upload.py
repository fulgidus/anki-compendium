"""
Tests for PDF upload endpoint.
"""
import json
from io import BytesIO
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.config import settings


class TestUploadEndpoint:
    """Test suite for PDF upload endpoint."""
    
    @pytest.mark.asyncio
    async def test_upload_valid_pdf(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading a valid PDF file."""
        # Create a minimal PDF file (mock)
        pdf_content = b"%PDF-1.4\n%EOF"
        
        files = {
            "file": ("test_document.pdf", BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "card_density": "medium",
            "subject": "Physics",
            "chapter": "Chapter 1"
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        job = response.json()
        assert job["source_filename"] == "test_document.pdf"
        assert job["status"] == "pending"
        assert job["progress"] == 0
        assert "id" in job
    
    @pytest.mark.asyncio
    async def test_upload_with_page_range(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading PDF with page range."""
        pdf_content = b"%PDF-1.4\n%EOF"
        
        files = {
            "file": ("document.pdf", BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "page_start": 1,
            "page_end": 10,
            "card_density": "high"
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        job = response.json()
        assert job["page_start"] == 1
        assert job["page_end"] == 10
    
    @pytest.mark.asyncio
    async def test_upload_with_custom_tags(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading PDF with custom tags."""
        pdf_content = b"%PDF-1.4\n%EOF"
        
        files = {
            "file": ("document.pdf", BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "custom_tags": json.dumps(["physics", "mechanics", "kinematics"])
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        job = response.json()
        assert job["settings"]["custom_tags"] == ["physics", "mechanics", "kinematics"]
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading non-PDF file fails."""
        txt_content = b"This is a text file"
        
        files = {
            "file": ("document.txt", BytesIO(txt_content), "text/plain")
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "application/pdf" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading file exceeding size limit fails."""
        # Create content larger than max size
        large_content = b"%PDF-1.4\n" + b"X" * (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1000)
        
        files = {
            "file": ("large.pdf", BytesIO(large_content), "application/pdf")
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    
    @pytest.mark.asyncio
    async def test_upload_invalid_page_range(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading with invalid page range fails."""
        pdf_content = b"%PDF-1.4\n%EOF"
        
        files = {
            "file": ("document.pdf", BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "page_start": 10,
            "page_end": 5  # Invalid: start > end
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "page" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_upload_invalid_custom_tags(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading with invalid custom tags fails."""
        pdf_content = b"%PDF-1.4\n%EOF"
        
        files = {
            "file": ("document.pdf", BytesIO(pdf_content), "application/pdf")
        }
        data = {
            "custom_tags": "not a json array"  # Invalid JSON
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files,
            data=data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "custom_tags" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_upload_without_auth(self, async_client: AsyncClient):
        """Test uploading without authentication fails."""
        pdf_content = b"%PDF-1.4\n%EOF"
        
        files = {
            "file": ("document.pdf", BytesIO(pdf_content), "application/pdf")
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            files=files
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_upload_empty_file(self, async_client: AsyncClient, auth_headers: dict):
        """Test uploading empty file fails."""
        empty_content = b""
        
        files = {
            "file": ("empty.pdf", BytesIO(empty_content), "application/pdf")
        }
        
        response = await async_client.post(
            f"{settings.API_V1_PREFIX}/upload",
            headers=auth_headers,
            files=files
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in response.json()["detail"].lower()
