"""
Storage service for MinIO/S3 integration.

Handles file uploads, downloads, and management in object storage.
"""
from datetime import timedelta
from io import BytesIO
from typing import BinaryIO, Optional
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.config import settings


class StorageService:
    """
    Storage service for MinIO/S3 object storage.
    
    Manages PDF uploads, deck storage, and presigned URL generation.
    """

    def __init__(self):
        """Initialize storage service."""
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.pdf_bucket = settings.MINIO_BUCKET_PDFS
        self.deck_bucket = settings.MINIO_BUCKET_DECKS

        # Ensure buckets exist
        self._ensure_buckets()

    def _ensure_buckets(self) -> None:
        """Create buckets if they don't exist."""
        for bucket in [self.pdf_bucket, self.deck_bucket]:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
            except S3Error:
                pass  # Bucket might already exist

    async def upload_pdf(
        self, user_id: UUID, filename: str, file_data: BinaryIO, file_size: int
    ) -> str:
        """
        Upload PDF file to storage.
        
        Args:
            user_id: User ID for file organization
            filename: Original filename
            file_data: File binary data
            file_size: File size in bytes
            
        Returns:
            Object path in storage
        """
        object_name = f"{user_id}/{filename}"

        self.client.put_object(
            self.pdf_bucket,
            object_name,
            file_data,
            file_size,
            content_type="application/pdf",
        )

        return object_name

    async def upload_deck(
        self, user_id: UUID, deck_id: UUID, filename: str, file_data: bytes
    ) -> str:
        """
        Upload Anki deck (.apkg) to storage.
        
        Args:
            user_id: User ID for file organization
            deck_id: Deck ID
            filename: Deck filename
            file_data: File binary data
            
        Returns:
            Object path in storage
        """
        object_name = f"{user_id}/{deck_id}/{filename}"

        self.client.put_object(
            self.deck_bucket,
            object_name,
            BytesIO(file_data),
            len(file_data),
            content_type="application/x-anki",
        )

        return object_name

    async def get_download_url(
        self, bucket: str, object_name: str, expires: timedelta = timedelta(minutes=15)
    ) -> str:
        """
        Generate presigned download URL.
        
        Args:
            bucket: Bucket name
            object_name: Object path in bucket
            expires: URL expiration time
            
        Returns:
            Presigned download URL
        """
        return self.client.presigned_get_object(bucket, object_name, expires=expires)

    async def delete_file(self, bucket: str, object_name: str) -> None:
        """
        Delete file from storage.
        
        Args:
            bucket: Bucket name
            object_name: Object path in bucket
        """
        try:
            self.client.remove_object(bucket, object_name)
        except S3Error:
            pass  # Object might not exist

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            bucket: Bucket name
            object_name: Object path in bucket
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False


# Singleton instance
storage_service = StorageService()
