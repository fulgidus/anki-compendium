"""
Pydantic schemas for Anki Compendium API.
"""
from app.schemas.common import (
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
    TimestampMixin,
    UUIDMixin,
)
from app.schemas.user import (
    AccountDeletion,
    PasswordChange,
    UserCreate,
    UserListResponse,
    UserPreferences,
    UserPreferencesUpdate,
    UserProfile,
    UserProfileUpdate,
    UserResponse,
    UserStats,
    UserUpdate,
)
from app.schemas.dashboard import (
    ActivityItem,
    DashboardStats,
)
from app.schemas.deck import (
    DeckCreate,
    DeckDownloadResponse,
    DeckListResponse,
    DeckResponse,
    DeckUpdate,
)
from app.schemas.job import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobStatusResponse,
    JobUpdate,
)
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    RegisterRequest,
    TokenData,
    TokenResponse,
)
from app.schemas.health import HealthResponse

__all__ = [
    # Common
    "MessageResponse",
    "PaginatedResponse",
    "PaginationParams",
    "TimestampMixin",
    "UUIDMixin",
    # User
    "AccountDeletion",
    "PasswordChange",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "UserProfileUpdate",
    "UserPreferences",
    "UserPreferencesUpdate",
    "UserStats",
    "UserListResponse",
    # Dashboard
    "ActivityItem",
    "DashboardStats",
    # Deck
    "DeckCreate",
    "DeckUpdate",
    "DeckResponse",
    "DeckListResponse",
    "DeckDownloadResponse",
    # Job
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "JobStatusResponse",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "PasswordResetRequest",
    "PasswordChangeRequest",
    "TokenResponse",
    "TokenData",
    # Health
    "HealthResponse",
]
