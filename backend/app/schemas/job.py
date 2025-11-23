"""
Job Pydantic schemas.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CardDensity(str, Enum):
    """Card generation density levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class JobBase(BaseModel):
    """Base job schema with common attributes."""
    source_filename: str
    # NOTE: Page range stored as page_start/page_end integers in DB, not as string
    settings: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class JobCreate(JobBase):
    """Schema for creating a new job."""
    user_id: UUID
    source_file_path: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    card_density: str = "medium"
    subject: Optional[str] = None
    chapter: Optional[str] = None
    custom_tags: Optional[list[str]] = None


class JobUpdate(BaseModel):
    """Schema for updating job status (internal use)."""
    status: Optional[str] = None
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None
    # NOTE: error_stack removed - does not exist in database
    result_deck_id: Optional[UUID] = None
    # NOTE: started_at removed - does not exist in database
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JobResponse(JobBase):
    """Schema for job response."""
    id: UUID
    user_id: UUID
    status: str
    progress_percent: int
    source_file_path: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    card_density: str
    subject: Optional[str] = None
    chapter: Optional[str] = None
    custom_tags: Optional[list[str]] = None
    result_deck_id: Optional[UUID] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    # NOTE: started_at removed - does not exist in database
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class JobCreateRequest(BaseModel):
    """Schema for job creation request (from upload endpoint)."""
    pdf_filename: str
    pdf_file_url: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    card_density: CardDensity = CardDensity.MEDIUM
    subject: Optional[str] = None
    chapter: Optional[str] = None
    custom_tags: Optional[list[str]] = None


class JobListResponse(BaseModel):
    """Paginated list of jobs."""
    total: int
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    items: list[JobResponse]


class JobStatusResponse(BaseModel):
    """Simplified job status response for polling."""
    id: UUID
    status: str
    progress: int
    error_message: Optional[str] = None
    result_deck_id: Optional[UUID] = None
