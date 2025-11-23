"""
Deck model for Anki flashcard deck metadata.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Integer, BigInteger, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Deck(Base):
    """
    Anki deck metadata model.
    
    Stores information about generated Anki decks including source PDF,
    card count, tags, and file location in MinIO.
    """
    __tablename__ = "decks"

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
    job_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Deck Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Source Information
    source_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    source_pages: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    # Card Statistics
    card_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    
    # File Storage
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    file_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True
    )
    
    # Metadata
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
        server_default="en"
    )
    tags: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True
    )
    settings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Timestamps
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
    last_downloaded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="decks"
    )
    job: Mapped[Optional["Job"]] = relationship(
        "Job",
        foreign_keys=[job_id]
    )

    def __repr__(self) -> str:
        return f"<Deck(id={self.id}, name={self.name}, cards={self.card_count})>"
