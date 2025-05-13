"""
Media Service

This service manages the creation, storage, and retrieval of media files (photos and videos)
and their associations with pets.
"""

from typing import BinaryIO, Dict, List, Optional, Union
from datetime import datetime
from werkzeug.datastructures import FileStorage
from sqlalchemy.orm import Session
import mimetypes
import tempfile
import os
from PIL import Image, ImageOps
import io
from pathlib import Path

from app.models import MediaFile, MediaType, Pet
from app.utils.cloud_storage import cloud_storage
from flask import current_app

class MediaService:
    """Service for managing media files (photos and videos)."""
    
    @staticmethod
    def upload_media(
        db_session: Session,
        file: FileStorage,
        title: str,
        description: Optional[str] = None,
        pet_ids: Optional[List[int]] = None,
        capture_date: Optional[datetime] = None,
        media_type: Optional[str] = None,
        bucket_name: Optional[str] = None
    ) -> MediaFile:
        """
        Upload a media file to cloud storage and save metadata in the database.
        
        Args:
            db_session: SQLAlchemy database session
            file: Uploaded file object
            title: Media title
            description: Optional description
            pet_ids: List of pet IDs to associate with this media
            capture_date: When the photo/video was taken
            media_type: Override auto-detected media type
            bucket_name: Override the default bucket name
            
        Returns:
            The created MediaFile instance
        """
        if bucket_name is None:
            # Get environment-specific bucket name
            env = current_app.config.get('ENV', 'dev')
            
            # Check flattened config first
            bucket_name = current_app.config.get(f'STORAGE_BUCKETS_MEDIA_{env.upper()}')
            
            # Fall back to default media bucket
            if not bucket_name:
                bucket_name = current_app.config.get('STORAGE_DEFAULT_MEDIA_BUCKET')
                
            # Check nested config if needed
            if not bucket_name and 'CONFIG' in current_app.config:
                nested_config = current_app.config['CONFIG']
                bucket_name = nested_config.get('storage', {}).get('buckets', {}).get(
                    'media', {}).get(env)
                
                if not bucket_name:
                    bucket_name = nested_config.get('storage', {}).get('default_media_bucket')
            
            # If still no bucket name, raise an error
            if not bucket_name:
                current_app.logger.error("No media bucket configured")
                raise ValueError("Media storage bucket not configured. Check application configuration.")
        
        # Auto-detect media type if not provided
        if not media_type:
            content_type = file.content_type
            if content_type and content_type.startswith('image/'):
                media_type = MediaType.PHOTO
            elif content_type and content_type.startswith('video/'):
                media_type = MediaType.VIDEO
            else:
                # Try to determine by filename extension
                ext = Path(file.filename).suffix.lower() if file.filename else ''
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
                    media_type = MediaType.PHOTO
                elif ext in ['.mp4', '.mov', '.avi', '.webm', '.mkv']:
                    media_type = MediaType.VIDEO
                else:
                    raise ValueError(f"Could not determine media type for file: {file.filename}")
        
        # Generate thumbnail for images
        thumbnail_key = None
        width = None
        height = None
        
        if media_type == MediaType.PHOTO:
            try:
                # Create a thumbnail and get image dimensions
                thumbnail_data, (width, height) = MediaService._create_thumbnail(file)
                
                # Upload thumbnail to cloud storage
                file_name = Path(file.filename).stem if file.filename else "media"
                thumbnail_name = f"{file_name}_thumb.jpg"
                
                # Reset file position to beginning before upload
                file.seek(0)
                
                # Upload thumbnail
                thumbnail_result = cloud_storage.upload_file(
                    file_obj=thumbnail_data,
                    original_filename=thumbnail_name,
                    bucket_name=bucket_name,
                    content_type='image/jpeg',
                    prefix="thumbnails"
                )
                
                thumbnail_key = thumbnail_result['object_key']
                
            except Exception as e:
                current_app.logger.error(f"Error creating thumbnail: {str(e)}")
                # Continue without thumbnail if there's an error
        
        # Upload the media file to cloud storage
        prefix = "photos" if media_type == MediaType.PHOTO else "videos"
        metadata = cloud_storage.upload_file(
            file_obj=file.stream,
            original_filename=file.filename,
            bucket_name=bucket_name,
            content_type=file.content_type,
            prefix=prefix
        )
        
        # Create media file record
        media_file = MediaFile(
            title=title,
            description=description,
            type=media_type,
            original_filename=metadata['original_filename'],
            object_key=metadata['object_key'],
            bucket_name=metadata['bucket_name'],
            content_type=metadata['content_type'],
            file_size=metadata['file_size'],
            thumbnail_key=thumbnail_key,
            width=width,
            height=height,
            upload_date=datetime.utcnow(),
            capture_date=capture_date
        )
        
        # Associate with pets if pet IDs provided
        if pet_ids:
            pets = db_session.query(Pet).filter(Pet.id.in_(pet_ids)).all()
            media_file.pets.extend(pets)
        
        # Save to database
        db_session.add(media_file)
        db_session.commit()
        
        return media_file
    
    @staticmethod
    def associate_with_pets(
        db_session: Session,
        media_id: int,
        pet_ids: List[int]
    ) -> bool:
        """
        Associate a media file with one or more pets.
        
        Args:
            db_session: SQLAlchemy database session
            media_id: ID of the media file
            pet_ids: List of pet IDs to associate with this media
            
        Returns:
            True if successful, False otherwise
        """
        try:
            media_file = db_session.query(MediaFile).get(media_id)
            if not media_file:
                return False
                
            # Find pets by IDs
            pets = db_session.query(Pet).filter(Pet.id.in_(pet_ids)).all()
            
            # Associate with pets
            for pet in pets:
                if pet not in media_file.pets:
                    media_file.pets.append(pet)
            
            db_session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error associating media with pets: {str(e)}")
            db_session.rollback()
            return False
    
    @staticmethod
    def remove_pet_association(
        db_session: Session,
        media_id: int,
        pet_id: int
    ) -> bool:
        """
        Remove an association between a media file and a pet.
        
        Args:
            db_session: SQLAlchemy database session
            media_id: ID of the media file
            pet_id: ID of the pet to disassociate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            media_file = db_session.query(MediaFile).get(media_id)
            pet = db_session.query(Pet).get(pet_id)
            
            if not media_file or not pet:
                return False
                
            if pet in media_file.pets:
                media_file.pets.remove(pet)
                db_session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error removing media-pet association: {str(e)}")
            db_session.rollback()
            return False
    
    @staticmethod
    def get_media_for_pet(
        db_session: Session,
        pet_id: int,
        media_type: Optional[str] = None
    ) -> List[MediaFile]:
        """
        Get all media files associated with a specific pet.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet
            media_type: Optional filter by media type (photo/video)
            
        Returns:
            List of MediaFile instances
        """
        query = db_session.query(MediaFile).join(
            MediaFile.pets
        ).filter(Pet.id == pet_id)
        
        if media_type:
            query = query.filter(MediaFile.type == media_type)
            
        return query.order_by(MediaFile.upload_date.desc()).all()
    
    @staticmethod
    def get_media_file(db_session: Session, media_id: int) -> Optional[MediaFile]:
        """
        Get a specific media file by ID.
        
        Args:
            db_session: SQLAlchemy database session
            media_id: ID of the media file
            
        Returns:
            MediaFile instance or None if not found
        """
        return db_session.query(MediaFile).get(media_id)
    
    @staticmethod
    def get_media_url(media_file: MediaFile, thumbnail: bool = False, expires_in: int = 3600) -> str:
        """
        Generate a temporary URL for a media file or its thumbnail.
        
        Args:
            media_file: The MediaFile instance
            thumbnail: Whether to get the thumbnail URL instead of the full media
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for the media file
        """
        if thumbnail and media_file.thumbnail_key:
            return cloud_storage.get_download_url(
                bucket_name=media_file.bucket_name,
                object_key=media_file.thumbnail_key,
                expires_in=expires_in
            )
        else:
            return cloud_storage.get_download_url(
                bucket_name=media_file.bucket_name,
                object_key=media_file.object_key,
                expires_in=expires_in
            )
    
    @staticmethod
    def delete_media(db_session: Session, media_id: int) -> bool:
        """
        Delete a media file from cloud storage and database.
        
        Args:
            db_session: SQLAlchemy database session
            media_id: ID of the media file to delete
            
        Returns:
            True if successful, False otherwise
        """
        media_file = db_session.query(MediaFile).get(media_id)
        
        if media_file is None:
            return False
        
        # Delete main file from cloud storage
        success = cloud_storage.delete_file(
            bucket_name=media_file.bucket_name,
            object_key=media_file.object_key
        )
        
        # Also delete thumbnail if it exists
        if success and media_file.thumbnail_key:
            cloud_storage.delete_file(
                bucket_name=media_file.bucket_name,
                object_key=media_file.thumbnail_key
            )
        
        if success:
            # Remove from database - the association table entries will be automatically deleted
            db_session.delete(media_file)
            db_session.commit()
            
        return success
    
    @staticmethod
    def _create_thumbnail(file: FileStorage, max_size: int = 300) -> tuple:
        """
        Create a thumbnail from an image file.
        
        Args:
            file: The image file
            max_size: Maximum dimension (width or height) for thumbnail
            
        Returns:
            Tuple of (file-like object of thumbnail data, (width, height) of original)
        """
        # Read the image
        img = Image.open(file)
        
        # Get original dimensions
        original_width, original_height = img.size
        
        # Create a thumbnail
        img.thumbnail((max_size, max_size))
        
        # Save to in-memory file
        thumb_io = io.BytesIO()
        
        # Handle RGBA images by converting to RGB
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            background.save(thumb_io, 'JPEG', quality=85)
        else:
            img.save(thumb_io, 'JPEG', quality=85)
        
        thumb_io.seek(0)
        
        return thumb_io, (original_width, original_height) 