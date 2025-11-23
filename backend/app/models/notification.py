"""
Notification model for push notification queue and history.
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotificationType(PyEnum):
    """Notification type enumeration."""
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    LIMIT_REACHED = "limit_reached"


class NotificationStatus(PyEnum):
    """Notification status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    """
    Notification model.
    
    Tracks push notifications sent to users for job completion,
    subscription changes, and limit warnings.
    """
    __tablename__ = "notifications"

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
    
    # Notification Information
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True
    )
    
    # Content
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Web Push Subscription
    push_subscription: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True
    )
    
    # Timestamps
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications"
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type.value}, status={self.status.value})>"
