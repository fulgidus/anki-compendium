"""
Audit log model for GDPR compliance and security tracking.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Text, DateTime, ForeignKey, BigInteger, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuditLog(Base):
    """
    Audit log model.
    
    Records user actions and system events for security, compliance, and debugging.
    Supports GDPR audit trail requirements.
    """
    __tablename__ = "audit_logs"

    # Primary Key
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    
    # Foreign Keys
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Action Information
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Request Context
    ip_address: Mapped[Optional[str]] = mapped_column(
        INET,
        nullable=True
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Additional Data (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    event_metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata",  # Keep DB column name as 'metadata'
        JSONB,
        nullable=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="audit_logs"
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
