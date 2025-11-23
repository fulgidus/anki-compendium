"""
User service for profile and preferences management.
"""
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.security import get_password_hash, verify_password
from app.models.deck import Deck
from app.models.user import User
from app.schemas.user import UserPreferences, UserStats


class UserService:
    """Service for user profile and preference operations."""
    
    @staticmethod
    async def get_user_stats(user_id: UUID, db: AsyncSession) -> UserStats:
        """
        Calculate user statistics.
        
        Args:
            user_id: UUID of the user
            db: Database session
            
        Returns:
            UserStats object with user statistics
        """
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Calculate total decks
            total_decks_result = await db.execute(
                select(func.count(Deck.id)).where(Deck.user_id == user_id)
            )
            total_decks = total_decks_result.scalar() or 0
            
            # Calculate total cards
            total_cards_result = await db.execute(
                select(func.sum(Deck.card_count)).where(Deck.user_id == user_id)
            )
            total_cards = total_cards_result.scalar() or 0
            
            return UserStats(
                total_decks=total_decks,
                total_cards=total_cards,
                member_since=user.created_at,
                last_login=user.last_login_at
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user stats for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user statistics"
            )
    
    @staticmethod
    async def get_preferences(user_id: UUID, db: AsyncSession) -> UserPreferences:
        """
        Get user preferences.
        
        Args:
            user_id: UUID of the user
            db: Database session
            
        Returns:
            UserPreferences object
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Return preferences or defaults
            if user.preferences:
                return UserPreferences(**user.preferences)
            else:
                # Return default preferences
                return UserPreferences()
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user preferences"
            )
    
    @staticmethod
    async def update_preferences(
        user_id: UUID,
        preferences_update: Dict,
        db: AsyncSession
    ) -> UserPreferences:
        """
        Update user preferences.
        
        Args:
            user_id: UUID of the user
            preferences_update: Dictionary of preferences to update
            db: Database session
            
        Returns:
            Updated UserPreferences object
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get current preferences or create new
            current_prefs = user.preferences or {}
            
            # Update with new values (only non-None values)
            for key, value in preferences_update.items():
                if value is not None:
                    current_prefs[key] = value
            
            # Update user preferences
            user.preferences = current_prefs
            await db.commit()
            await db.refresh(user)
            
            return UserPreferences(**user.preferences)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user preferences"
            )
    
    @staticmethod
    async def update_profile(
        user_id: UUID,
        display_name: Optional[str],
        db: AsyncSession
    ) -> User:
        """
        Update user profile.
        
        Args:
            user_id: UUID of the user
            display_name: New display name (optional)
            db: Database session
            
        Returns:
            Updated User object
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields
            if display_name is not None:
                user.display_name = display_name
            
            await db.commit()
            await db.refresh(user)
            
            return user
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
    
    @staticmethod
    async def change_password(
        user_id: UUID,
        current_password: str,
        new_password: str,
        db: AsyncSession
    ) -> bool:
        """
        Change user password.
        
        Note: In a Keycloak-based system, password management should ideally
        be handled through Keycloak's API. This is a placeholder for systems
        that manage passwords locally.
        
        Args:
            user_id: UUID of the user
            current_password: Current password for verification
            new_password: New password to set
            db: Database session
            
        Returns:
            True if password was changed successfully
        """
        # TODO: Implement Keycloak password change via Keycloak Admin API
        # For now, return error as passwords are managed by Keycloak
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password management is handled through Keycloak. Please use the password reset functionality."
        )
    
    @staticmethod
    async def delete_user_data(user_id: UUID, db: AsyncSession) -> bool:
        """
        Delete all user data (soft delete).
        
        This performs a soft delete by setting deleted_at timestamp.
        Actual data cleanup should be handled by a background job.
        
        Args:
            user_id: UUID of the user
            db: Database session
            
        Returns:
            True if user was deleted successfully
        """
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            if user.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is already deleted"
                )
            
            # Soft delete: set deleted_at timestamp
            user.deleted_at = datetime.utcnow()
            user.is_active = False
            
            await db.commit()
            
            logger.info(f"User {user_id} marked for deletion")
            
            # TODO: Trigger background job to delete associated data (decks, jobs)
            # from MinIO and perform full cleanup
            
            return True
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user account"
            )


# Singleton instance
user_service = UserService()
