"""
User Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    keycloak_id: str = Field(..., description="Keycloak user ID")


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = None
    display_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    keycloak_id: str
    subscription_tier: str
    cards_generated_month: int
    cards_limit_month: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None


class UserProfile(UserResponse):
    """Extended user profile with additional details."""
    deleted_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """Paginated list of users."""
    total: int
    skip: int
    limit: int
    items: list[UserResponse]


class UserStats(BaseModel):
    """User statistics schema."""
    total_decks: int = Field(..., description="Total number of decks created by user")
    total_cards: int = Field(..., description="Total number of flashcards across all decks")
    member_since: datetime = Field(..., description="Date when user account was created")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserPreferences(BaseModel):
    """User preferences schema."""
    default_max_cards: int = Field(20, ge=1, le=100, description="Default maximum number of cards per deck")
    default_difficulty: str = Field("medium", pattern="^(easy|medium|hard)$", description="Default difficulty level")
    include_images: bool = Field(True, description="Include images in flashcards by default")
    email_on_completion: bool = Field(True, description="Send email notification when job completes")
    email_on_failure: bool = Field(True, description="Send email notification when job fails")

    model_config = ConfigDict(from_attributes=True)


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    default_max_cards: Optional[int] = Field(None, ge=1, le=100)
    default_difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    include_images: Optional[bool] = None
    email_on_completion: Optional[bool] = None
    email_on_failure: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    display_name: Optional[str] = Field(None, max_length=255, description="User's display name")

    model_config = ConfigDict(from_attributes=True)


class PasswordChange(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")

    model_config = ConfigDict(from_attributes=True)


class AccountDeletion(BaseModel):
    """Schema for account deletion confirmation."""
    confirmation: str = Field(..., description="User must type 'DELETE' to confirm account deletion")

    model_config = ConfigDict(from_attributes=True)
