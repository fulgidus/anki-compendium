"""
User profile and preferences API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    AccountDeletion,
    PasswordChange,
    UserPreferences,
    UserPreferencesUpdate,
    UserProfile,
    UserProfileUpdate,
    UserStats,
)
from app.services.user_service import user_service

router = APIRouter()


@router.get("/profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current user's profile information.
    
    Returns complete profile including:
    - User ID, email, username, display name
    - Subscription tier and card limits
    - Account status and timestamps
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: User profile object
    - 401: Unauthorized (invalid or missing token)
    """
    try:
        logger.info(f"Fetching profile for user {current_user.id}")
        return UserProfile.model_validate(current_user)
    
    except Exception as e:
        logger.error(f"Error fetching profile for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/profile", response_model=UserProfile, status_code=status.HTTP_200_OK)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's profile.
    
    Allows updating:
    - Display name
    
    Note: Email changes should be handled through Keycloak/auth provider.
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: Updated user profile
    - 400: Invalid request data
    - 401: Unauthorized
    - 500: Internal server error
    """
    try:
        logger.info(f"Updating profile for user {current_user.id}")
        
        updated_user = await user_service.update_profile(
            user_id=current_user.id,
            display_name=profile_update.display_name,
            db=db
        )
        
        return UserProfile.model_validate(updated_user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get("/stats", response_model=UserStats, status_code=status.HTTP_200_OK)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for the current user.
    
    Returns:
    - Total decks created
    - Total flashcards across all decks
    - Member since date
    - Last login timestamp
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: User statistics object
    - 401: Unauthorized
    - 500: Internal server error
    """
    try:
        logger.info(f"Fetching stats for user {current_user.id}")
        stats = await user_service.get_user_stats(current_user.id, db)
        return stats
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats for user {current_user.id}: {str(e)}")
        raise


@router.get("/preferences", response_model=UserPreferences, status_code=status.HTTP_200_OK)
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's preferences.
    
    Returns user preferences including:
    - Default maximum cards per deck
    - Default difficulty level
    - Image inclusion preference
    - Email notification settings
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: User preferences object (with defaults if not set)
    - 401: Unauthorized
    - 500: Internal server error
    """
    try:
        logger.info(f"Fetching preferences for user {current_user.id}")
        prefs = await user_service.get_preferences(current_user.id, db)
        return prefs
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching preferences for user {current_user.id}: {str(e)}")
        raise


@router.put("/preferences", response_model=UserPreferences, status_code=status.HTTP_200_OK)
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's preferences.
    
    Allows updating any of:
    - default_max_cards: Default maximum cards (1-100)
    - default_difficulty: Default difficulty (easy, medium, hard)
    - include_images: Include images in flashcards
    - email_on_completion: Email notification for job completion
    - email_on_failure: Email notification for job failures
    
    Only provided fields will be updated; others remain unchanged.
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: Updated user preferences
    - 400: Invalid preference values
    - 401: Unauthorized
    - 500: Internal server error
    """
    try:
        logger.info(f"Updating preferences for user {current_user.id}")
        
        # Convert Pydantic model to dict, excluding None values
        prefs_dict = preferences.model_dump(exclude_none=True)
        
        updated_prefs = await user_service.update_preferences(
            user_id=current_user.id,
            preferences_update=prefs_dict,
            db=db
        )
        
        return updated_prefs
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating preferences for user {current_user.id}: {str(e)}")
        raise


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change the current user's password.
    
    Note: Password management is handled through Keycloak.
    This endpoint is not implemented and will return 501.
    Use the password reset flow through the auth provider instead.
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 501: Not implemented (passwords managed by Keycloak)
    - 401: Unauthorized
    """
    try:
        logger.info(f"Password change requested for user {current_user.id}")
        
        await user_service.change_password(
            user_id=current_user.id,
            current_password=password_change.current_password,
            new_password=password_change.new_password,
            db=db
        )
        
        return {"message": "Password changed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {current_user.id}: {str(e)}")
        raise


@router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_account(
    confirmation: AccountDeletion,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete the current user's account and all associated data.
    
    This performs a soft delete by marking the account as deleted.
    A background job will handle cleanup of:
    - All decks (from MinIO storage)
    - All jobs
    - All user data
    
    **Confirmation Required:** User must provide confirmation="DELETE"
    
    **Authentication Required:** Yes
    
    **Returns:**
    - 200: Account deletion initiated
    - 400: Invalid confirmation or account already deleted
    - 401: Unauthorized
    - 500: Internal server error
    
    **Warning:** This action cannot be undone!
    """
    try:
        logger.warning(f"Account deletion requested for user {current_user.id}")
        
        # Validate confirmation
        if confirmation.confirmation != "DELETE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation. Please type 'DELETE' to confirm account deletion."
            )
        
        success = await user_service.delete_user_data(
            user_id=current_user.id,
            db=db
        )
        
        if success:
            logger.warning(f"Account deleted for user {current_user.id}")
            return {
                "message": "Account deletion initiated. Your account and all data will be permanently deleted.",
                "user_id": str(current_user.id)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account for user {current_user.id}: {str(e)}")
        raise
