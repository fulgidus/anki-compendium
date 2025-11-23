"""
Job model for PDF processing job tracking.
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Integer, BigInteger, Text, DateTime, ForeignKey, Enum, func, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobStatus(PyEnum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    """
    PDF processing job model.
    
    Tracks the status and progress of flashcard generation jobs.
    Contains source file information, processing settings, and error handling.
    """
    __tablename__ = "jobs"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid()
    )
    
    # Foreign Keys
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    result_deck_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("decks.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Status & Progress
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=JobStatus.PENDING,
        index=True
    )
    progress_percent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    
    # Source File Information
    source_filename: Mapped[str] = mapped_column(
        "pdf_filename",
        String(255),
        nullable=False
    )
    source_file_path: Mapped[str] = mapped_column(
        "pdf_file_url",
        String(500),
        nullable=False
    )
    
    # Page Range (optional subset of PDF)
    page_start: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    page_end: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    
    # Processing Settings
    card_density: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        server_default="medium"
    )
    subject: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    chapter: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    custom_tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String),
        nullable=True
    )
    
    # DEPRECATED: Legacy settings field (keep for backward compatibility)
    # NOTE: Use specific fields above (card_density, subject, etc.) instead
    settings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Error Handling
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
#    error_stack: Mapped[Optional[str]] = mapped_column(
#        Text,
#        nullable=True
#    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    max_retries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3"
    )
    
    # Timestamps
#    started_at: Mapped[Optional[datetime]] = mapped_column(
#        DateTime(timezone=True),
#        nullable=True
#    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="jobs"
    )
    result_deck: Mapped[Optional["Deck"]] = relationship(
        "Deck",
        foreign_keys=[result_deck_id]
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, status={self.status.value}, progress={self.progress_percent}%)>"
