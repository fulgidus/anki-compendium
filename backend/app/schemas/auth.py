"""
Authentication and authorization schemas.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    user_id: Optional[str] = None
    email: Optional[str] = None
    sub: Optional[str] = None  # Keycloak subject
    roles: list[str] = []


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class LoginResponse(BaseModel):
    """Login response with tokens and user info."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")
    display_name: Optional[str] = Field(None, max_length=255)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must contain only alphanumeric characters, hyphens, and underscores")
        return v


class RegisterResponse(BaseModel):
    """Registration response."""
    user: UserResponse
    message: str = "User registered successfully"


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Valid refresh token")


class LogoutRequest(BaseModel):
    """Logout request (optional body for additional data)."""
    refresh_token: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    old_password: str
    new_password: str = Field(..., min_length=8)
