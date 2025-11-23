"""
File validation utilities for upload endpoints.

Provides validation for file types, sizes, and filename sanitization.
"""
import re
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status


def validate_pdf_file(file: UploadFile, max_size_mb: int) -> None:
    """
    Validate uploaded file is PDF and within size limit.
    
    Args:
        file: Uploaded file from FastAPI
        max_size_mb: Maximum allowed file size in megabytes
        
    Raises:
        HTTPException: If validation fails
    """
    # Check content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Expected application/pdf, got {file.content_type}"
        )
    
    # Check file extension
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have .pdf extension"
        )


async def validate_file_size(file: UploadFile, max_size_mb: int) -> int:
    """
    Validate file size and return the size in bytes.
    
    Args:
        file: Uploaded file from FastAPI
        max_size_mb: Maximum allowed file size in megabytes
        
    Returns:
        File size in bytes
        
    Raises:
        HTTPException: If file exceeds size limit
    """
    # Read file content to check size
    content = await file.read()
    file_size = len(content)
    
    # Reset file pointer for later reading
    await file.seek(0)
    
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {file_size / 1024 / 1024:.2f}MB exceeds maximum allowed size of {max_size_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    return file_size


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize filename for safe storage.
    
    Removes path components, replaces unsafe characters,
    and limits length while preserving extension.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length (default 200)
        
    Returns:
        Sanitized filename
        
    Raises:
        HTTPException: If filename is invalid after sanitization
    """
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty"
        )
    
    # Get basename to remove path components
    filename = Path(filename).name
    
    # Split name and extension
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    
    # Remove or replace unsafe characters
    # Allow: alphanumeric, spaces, hyphens, underscores, dots
    stem = re.sub(r'[^\w\s\-\.]', '_', stem)
    
    # Replace multiple spaces/underscores with single underscore
    stem = re.sub(r'[\s_]+', '_', stem)
    
    # Remove leading/trailing underscores and dots
    stem = stem.strip('_.')
    
    if not stem:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename contains no valid characters"
        )
    
    # Limit length while preserving extension
    max_stem_length = max_length - len(suffix)
    if len(stem) > max_stem_length:
        stem = stem[:max_stem_length]
    
    sanitized = f"{stem}{suffix}"
    
    return sanitized


def generate_unique_filename(user_id: str, original_filename: str) -> str:
    """
    Generate unique filename for storage.
    
    Combines timestamp, user ID, and sanitized original filename
    to create a unique storage path.
    
    Args:
        user_id: User UUID as string
        original_filename: Original uploaded filename
        
    Returns:
        Unique filename for storage
    """
    from datetime import datetime
    from uuid import uuid4
    
    sanitized = sanitize_filename(original_filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid4())[:8]
    
    stem = Path(sanitized).stem
    suffix = Path(sanitized).suffix
    
    # Format: timestamp_uniqueid_originalname.ext
    unique_filename = f"{timestamp}_{unique_id}_{stem}{suffix}"
    
    return unique_filename


def validate_page_range(page_start: int | None = None, page_end: int | None = None) -> None:
    """
    Validate page range parameters.
    
    Args:
        page_start: Starting page number (1-indexed)
        page_end: Ending page number (1-indexed)
        
    Raises:
        HTTPException: If page range is invalid
    """
    if page_start is not None and page_start < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page_start must be >= 1"
        )
    
    if page_end is not None and page_end < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page_end must be >= 1"
        )
    
    if page_start is not None and page_end is not None:
        if page_start > page_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="page_start cannot be greater than page_end"
            )
