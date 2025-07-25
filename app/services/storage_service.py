import os
import aiofiles
from pathlib import Path
from typing import Optional
import uuid
from urllib.parse import urlparse
import boto3
from botocore.exceptions import ClientError
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.config import settings


class StorageService:
    """Service for handling file storage operations."""
    
    def __init__(self):
        self.storage_type = settings.storage_type
        self.local_storage_path = Path(settings.local_storage_path)
        
        if self.storage_type == "s3":
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            self.bucket_name = settings.s3_bucket_name
        
        # Create local storage directory if it doesn't exist
        if self.storage_type == "local":
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
    
    async def store_media(self, media_content: bytes, job_id: uuid.UUID, file_extension: str = "jpg") -> tuple[str, str]:
        """
        Store media content and return (public_url, storage_path).
        
        Args:
            media_content: The media file content as bytes
            job_id: Unique job identifier
            file_extension: File extension (without dot)
        
        Returns:
            tuple: (public_url, storage_path)
        """
        filename = f"{job_id}.{file_extension}"
        
        if self.storage_type == "local":
            return await self._store_local(media_content, filename)
        elif self.storage_type == "s3":
            return await self._store_s3(media_content, filename)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    async def _store_local(self, media_content: bytes, filename: str) -> tuple[str, str]:
        """Store file locally."""
        file_path = self.local_storage_path / filename
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(media_content)
        
        # Return relative URL and absolute path
        public_url = f"/media/{filename}"
        storage_path = str(file_path)
        
        return public_url, storage_path
    
    async def _store_s3(self, media_content: bytes, filename: str) -> tuple[str, str]:
        """Store file in S3."""
        key = f"media/{filename}"
        
        # Use ThreadPoolExecutor for S3 upload since boto3 is not async
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(
                executor,
                self._upload_to_s3,
                media_content,
                key
            )
        
        # Generate public URL
        public_url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
        storage_path = f"s3://{self.bucket_name}/{key}"
        
        return public_url, storage_path
    
    def _upload_to_s3(self, media_content: bytes, key: str) -> None:
        """Synchronous S3 upload."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=media_content,
                ContentType="image/jpeg"  # Assume JPEG for now
            )
        except ClientError as e:
            raise Exception(f"Failed to upload to S3: {e}")
    
    async def delete_media(self, storage_path: str) -> bool:
        """Delete media file from storage."""
        try:
            if self.storage_type == "local":
                return await self._delete_local(storage_path)
            elif self.storage_type == "s3":
                return await self._delete_s3(storage_path)
            return False
        except Exception:
            return False
    
    async def _delete_local(self, storage_path: str) -> bool:
        """Delete local file."""
        try:
            file_path = Path(storage_path)
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception:
            return False
    
    async def _delete_s3(self, storage_path: str) -> bool:
        """Delete S3 object."""
        try:
            # Parse S3 path: s3://bucket/key
            parsed = urlparse(storage_path)
            bucket = parsed.netloc
            key = parsed.path.lstrip('/')
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(
                    executor,
                    self.s3_client.delete_object,
                    {"Bucket": bucket, "Key": key}
                )
            return True
        except Exception:
            return False
    
    def get_file_extension_from_url(self, url: str) -> str:
        """Extract file extension from URL."""
        parsed = urlparse(url)
        path = Path(parsed.path)
        extension = path.suffix.lstrip('.')
        return extension if extension else "jpg" 