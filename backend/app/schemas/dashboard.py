"""
Dashboard Pydantic schemas.
"""
from datetime import datetime
from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardStats(BaseModel):
    """Dashboard statistics schema."""
    total_decks: int = Field(..., description="Total number of decks created by user")
    total_cards: int = Field(..., description="Total number of flashcards across all decks")
    active_jobs: int = Field(..., description="Number of jobs currently pending or processing")
    decks_this_week: int = Field(..., description="Number of decks created in the last 7 days")
    decks_this_month: int = Field(..., description="Number of decks created in the last 30 days")

    model_config = ConfigDict(from_attributes=True)


class ActivityItem(BaseModel):
    """Activity item schema for recent user activity."""
    id: UUID = Field(..., description="Unique identifier (job ID or deck ID)")
    type: Literal['job', 'deck'] = Field(..., description="Type of activity item")
    title: str = Field(..., description="Display title for the activity")
    timestamp: datetime = Field(..., description="When the activity occurred")
    status: Optional[str] = Field(None, description="Status for job type items")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(from_attributes=True)
