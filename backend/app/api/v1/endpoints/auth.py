"""
Authentication endpoints for user registration, login, and token management.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    verify_token
)
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a user account in both Keycloak and the local database.
    
    **Requirements:**
    - Email must be valid and unique
    - Username must be 3-50 characters, alphanumeric with hyphens/underscores
    - Password must be at least 8 characters
    
    **Returns:**
    - User profile information
    - Success message
    """
    try:
        user = await auth_service.register(
            email=request.email,
            username=request.username,
            password=request.password,
            display_name=request.display_name,
            db=db
        )
        
        return RegisterResponse(
            user=UserResponse.model_validate(user),
            message="User registered successfully. Please check your email to verify your account."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access tokens.
    
    Validates credentials against Keycloak and returns JWT tokens
    for accessing protected endpoints.
    
    **Returns:**
    - Access token (short-lived, for API requests)
    - Refresh token (long-lived, for obtaining new access tokens)
    - User profile information
    """
    try:
        # Authenticate with Keycloak and sync user
        keycloak_tokens, user = await auth_service.login(
            email=request.email,
            password=request.password,
            db=db
        )
        
        # Create application JWT tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Validates the refresh token and issues a new access token.
    Refresh tokens have a longer expiration time than access tokens.
    
    **Returns:**
    - New access token
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Expected refresh token."
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user exists and is active
        from uuid import UUID
        from sqlalchemy import select
        
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if user.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account has been deleted"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during token refresh"
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    logout_request: LogoutRequest = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user.
    
    Invalidates the user's Keycloak session if a refresh token is provided.
    The client should also discard stored tokens.
    
    **Optional:**
    - refresh_token: If provided, will be revoked in Keycloak
    """
    try:
        if logout_request and logout_request.refresh_token:
            await auth_service.logout(logout_request.refresh_token)
        
        logger.info(f"User logged out: {current_user.email}")
        
    except Exception as e:
        # Log error but don't fail logout
        logger.error(f"Error during logout: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.
    
    Returns the profile of the currently authenticated user.
    Requires a valid access token in the Authorization header.
    
    **Returns:**
    - Complete user profile
    - Subscription tier and limits
    - Usage statistics
    """
    return UserResponse.model_validate(current_user)


@router.post("/verify-token")
async def verify_token_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify if the provided token is valid.
    
    Useful for checking token validity without fetching full user details.
    
    **Returns:**
    - valid: True if token is valid
    - user_id: UUID of the authenticated user
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email
    }
