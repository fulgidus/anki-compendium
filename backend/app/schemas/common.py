"""
Common Pydantic schemas and base classes.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TimestampMixin(BaseModel):
    """Mixin for models with created_at and updated_at timestamps."""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UUIDMixin(BaseModel):
    """Mixin for models with UUID primary key."""
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    total: int
    skip: int
    limit: int
    items: list


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    detail: Optional[str] = None
