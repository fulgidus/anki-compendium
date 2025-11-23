"""
Deck service for Anki deck management.

Handles deck creation, retrieval, and deletion.
"""
from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.deck import Deck
from app.schemas.deck import DeckCreate, DeckUpdate
from app.services.storage_service import storage_service


class DeckService:
    """
    Deck service for managing Anki decks.
    
    Handles deck metadata and file references.
    """

    async def create_deck(self, db: AsyncSession, deck_data: DeckCreate) -> Deck:
        """
        Create a new deck.
        
        Args:
            db: Database session
            deck_data: Deck creation data
            
        Returns:
            Created deck instance
        """
        deck = Deck(**deck_data.model_dump())

        db.add(deck)
        await db.commit()
        await db.refresh(deck)

        return deck

    async def get_deck(self, db: AsyncSession, deck_id: UUID) -> Optional[Deck]:
        """
        Get deck by ID.
        
        Args:
            db: Database session
            deck_id: Deck ID
            
        Returns:
            Deck instance or None
        """
        result = await db.execute(select(Deck).where(Deck.id == deck_id))
        return result.scalar_one_or_none()

    async def get_user_decks(
        self,
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[Deck], int]:
        """
        Get paginated decks for user.
        
        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (list of decks, total count)
        """
        # Get total count
        count_result = await db.execute(
            select(func.count()).select_from(Deck).where(Deck.user_id == user_id)
        )
        total = count_result.scalar_one()

        # Get paginated results
        result = await db.execute(
            select(Deck)
            .where(Deck.user_id == user_id)
            .order_by(Deck.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        decks = list(result.scalars().all())

        return decks, total

    async def update_deck(
        self, db: AsyncSession, deck_id: UUID, deck_update: DeckUpdate
    ) -> Optional[Deck]:
        """
        Update deck metadata.
        
        Args:
            db: Database session
            deck_id: Deck ID
            deck_update: Deck update data
            
        Returns:
            Updated deck instance or None
        """
        deck = await self.get_deck(db, deck_id)
        if not deck:
            return None

        update_data = deck_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deck, field, value)

        await db.commit()
        await db.refresh(deck)

        return deck

    async def delete_deck(self, db: AsyncSession, deck_id: UUID) -> bool:
        """
        Delete deck.
        
        Args:
            db: Database session
            deck_id: Deck ID
            
        Returns:
            True if deleted, False if not found
        """
        deck = await self.get_deck(db, deck_id)
        if not deck:
            return False

        await db.delete(deck)
        await db.commit()

        return True

    async def verify_ownership(
        self, db: AsyncSession, deck_id: UUID, user_id: UUID
    ) -> bool:
        """
        Verify that a deck belongs to a specific user.
        
        Args:
            db: Database session
            deck_id: Deck ID
            user_id: User ID
            
        Returns:
            True if user owns deck, False otherwise
        """
        result = await db.execute(
            select(Deck).where(Deck.id == deck_id, Deck.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_download_url(
        self,
        deck: Deck,
        expires_in: int = 3600
    ) -> str:
        """
        Get presigned download URL for deck.
        
        Args:
            deck: Deck instance
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned download URL
        """
        url = await storage_service.get_download_url(
            bucket=settings.MINIO_BUCKET_DECKS,
            object_name=deck.file_path,
            expires=timedelta(seconds=expires_in)
        )
        return url

    async def delete_deck_with_file(
        self,
        db: AsyncSession,
        deck_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete deck and associated file from storage.
        
        Args:
            db: Database session
            deck_id: Deck ID
            user_id: User ID for ownership verification
            
        Raises:
            HTTPException: If deck not found or not owned by user
        """
        # Get deck
        deck = await self.get_deck(db, deck_id)
        if not deck:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deck not found"
            )
        
        # Verify ownership
        if deck.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this deck"
            )
        
        # Delete file from storage
        try:
            await storage_service.delete_file(
                bucket=settings.MINIO_BUCKET_DECKS,
                object_name=deck.file_path
            )
        except Exception as e:
            # Log error but continue with database deletion
            # File might already be deleted or storage might be unavailable
            pass
        
        # Delete from database
        await db.delete(deck)
        await db.commit()


# Singleton instance
deck_service = DeckService()
