"""
Deck Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class DeckBase(BaseModel):
    """Base deck schema with common attributes."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    language: str = Field(default="en", pattern="^[a-z]{2}$")

    model_config = ConfigDict(from_attributes=True)


class DeckCreate(DeckBase):
    """Schema for creating a new deck (usually from job completion)."""
    user_id: UUID
    job_id: Optional[UUID] = None
    source_filename: str
    source_pages: Optional[str] = None
    card_count: int = 0
    file_path: str
    file_size_bytes: Optional[int] = None
    settings: Optional[dict] = None


class DeckUpdate(BaseModel):
    """Schema for updating deck metadata."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[list[str]] = None

    model_config = ConfigDict(from_attributes=True)


class DeckResponse(DeckBase):
    """Schema for deck response."""
    id: UUID
    user_id: UUID
    job_id: Optional[UUID] = None
    source_filename: str
    source_pages: Optional[str] = None
    card_count: int
    file_path: str
    file_size_bytes: Optional[int] = None
    settings: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    last_downloaded_at: Optional[datetime] = None


class DeckListResponse(BaseModel):
    """Paginated list of decks."""
    total: int
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    items: list[DeckResponse]


class DeckDownloadResponse(BaseModel):
    """Schema for deck download URL response."""
    download_url: str
    expires_in: int = Field(..., description="URL expiry time in seconds")
