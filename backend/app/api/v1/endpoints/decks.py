"""
Deck management endpoints for Anki deck retrieval and downloads.
"""
import math
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.deck import DeckDownloadResponse, DeckListResponse, DeckResponse
from app.services.deck_service import deck_service

router = APIRouter()


@router.get("/", response_model=DeckListResponse)
async def list_decks(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all generated Anki decks for the current user with pagination.
    
    **Query Parameters:**
    - page: Page number (1-indexed, default=1)
    - page_size: Items per page (default=20, max=100)
    
    **Returns:**
    - Paginated list of decks with metadata
    - Deck information including card count and file size
    
    **Example:**
    ```bash
    # Get all decks, page 1
    GET /api/v1/decks?page=1&page_size=20
    
    # Get first 50 decks
    GET /api/v1/decks?page=1&page_size=50
    ```
    """
    # Get decks from service
    decks, total = await deck_service.get_user_decks(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return DeckListResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=total_pages,
        items=[DeckResponse.model_validate(deck) for deck in decks]
    )


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific Anki deck.
    
    **Path Parameters:**
    - deck_id: UUID of the deck
    
    **Returns:**
    - Complete deck details including metadata, card count, and file info
    
    **Errors:**
    - 404: Deck not found
    - 403: Not authorized to access this deck
    
    **Example:**
    ```bash
    GET /api/v1/decks/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    # Get deck
    deck = await deck_service.get_deck(db, deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Verify ownership
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this deck"
        )
    
    return DeckResponse.model_validate(deck)


@router.get("/{deck_id}/download", response_model=DeckDownloadResponse)
async def get_deck_download_url(
    deck_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a presigned download URL for an Anki deck (.apkg file).
    
    The URL is temporary and expires after 1 hour for security.
    Use this URL to download the deck file directly from storage.
    
    **Path Parameters:**
    - deck_id: UUID of the deck to download
    
    **Returns:**
    - download_url: Presigned URL valid for 1 hour
    - expires_in: Seconds until URL expires (3600)
    
    **Errors:**
    - 404: Deck not found
    - 403: Not authorized to download this deck
    
    **Example:**
    ```bash
    # Get download URL
    GET /api/v1/decks/550e8400-e29b-41d4-a716-446655440000/download
    
    # Response:
    {
      "download_url": "https://minio.example.com/decks/...",
      "expires_in": 3600
    }
    
    # Download the file
    curl -O "download_url"
    ```
    """
    # Get deck
    deck = await deck_service.get_deck(db, deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Verify ownership
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this deck"
        )
    
    # Generate presigned download URL (expires in 1 hour)
    expires_in = 3600  # 1 hour
    try:
        download_url = await deck_service.get_download_url(
            deck=deck,
            expires_in=expires_in
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )
    
    # Update last_downloaded_at timestamp
    deck.last_downloaded_at = datetime.utcnow()
    await db.commit()
    
    return DeckDownloadResponse(
        download_url=download_url,
        expires_in=expires_in
    )


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an Anki deck and its associated file from storage.
    
    This action is permanent and cannot be undone.
    The deck file will be removed from object storage and
    the database record will be deleted.
    
    **Path Parameters:**
    - deck_id: UUID of the deck to delete
    
    **Returns:**
    - 204 No Content on success
    
    **Errors:**
    - 404: Deck not found
    - 403: Not authorized to delete this deck
    
    **Example:**
    ```bash
    DELETE /api/v1/decks/550e8400-e29b-41d4-a716-446655440000
    ```
    """
    await deck_service.delete_deck_with_file(
        db=db,
        deck_id=deck_id,
        user_id=current_user.id
    )
    
    return None
