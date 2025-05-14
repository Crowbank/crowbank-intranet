"""
Cloud Storage Utilities for Cloudflare R2 Integration

This module provides utilities for interacting with Cloudflare R2 object storage,
which is S3-compatible. It handles uploading, downloading, and managing files in the cloud.
"""

import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import BinaryIO, Dict, Optional, Tuple, Union
import mimetypes
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


class CloudStorageService:
    """Service for interacting with Cloudflare R2 cloud storage."""
    
    def __init__(self, app=None):
        """Initialize the storage service, optionally with a Flask app."""
        self.client = None
        self.resource = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app configuration."""
        # Get config from app
        r2_account_id = app.config.get('R2_ACCOUNT_ID')
        r2_access_key = app.config.get('R2_ACCESS_KEY')
        r2_secret_key = app.config.get('R2_SECRET_KEY')
        r2_region = app.config.get('R2_REGION', 'auto')
        
        # Setup endpoint URL for R2
        endpoint_url = f"https://{r2_account_id}.r2.cloudflarestorage.com"
        
        # Initialize S3 client (R2 is S3-compatible)
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            region_name=r2_region,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key
        )
        
        self.resource = boto3.resource(
            's3',
            endpoint_url=endpoint_url,
            region_name=r2_region,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key
        )
    
    def _get_bucket(self, bucket_name):
        """Get a bucket by name."""
        return self.resource.Bucket(bucket_name)
    
    def upload_file(
        self, 
        file_obj: BinaryIO, 
        original_filename: str, 
        bucket_name: str,
        content_type: Optional[str] = None,
        prefix: Optional[str] = None
    ) -> Dict:
        """
        Upload a file to R2 storage.
        
        Args:
            file_obj: File-like object to upload
            original_filename: Original filename from the user
            bucket_name: Target bucket name
            content_type: Optional MIME type, detected if not provided
            prefix: Optional prefix (folder) to prepend to the object key
            
        Returns:
            Dictionary with object metadata
        """
        # Generate a safe filename to use as the base for the object key
        secure_name = secure_filename(original_filename)
        
        # Auto-detect content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type:
                content_type = 'application/octet-stream'
        
        # Generate a unique object key by adding uuid
        # Format: prefix/yyyy-mm-dd/uuid-secure_name
        date_prefix = datetime.utcnow().strftime('%Y-%m-%d')
        unique_id = str(uuid.uuid4())
        
        if prefix:
            object_key = f"{prefix}/{date_prefix}/{unique_id}-{secure_name}"
        else:
            object_key = f"{date_prefix}/{unique_id}-{secure_name}"
        
        try:
            # Upload the file to R2
            self.client.upload_fileobj(
                file_obj,
                bucket_name,
                object_key,
                ExtraArgs={
                    'ContentType': content_type
                }
            )
            
            # Get object info
            head = self.client.head_object(
                Bucket=bucket_name,
                Key=object_key
            )
            
            # Return metadata
            return {
                'original_filename': original_filename,
                'object_key': object_key,
                'bucket_name': bucket_name,
                'content_type': content_type,
                'file_size': head.get('ContentLength', 0),
                'last_modified': head.get('LastModified')
            }
            
        except ClientError as e:
            current_app.logger.error(f"Error uploading to R2: {str(e)}")
            raise
    
    def get_download_url(self, bucket_name: str, object_key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL to download a file.
        
        Args:
            bucket_name: The bucket containing the object
            object_key: The key of the object to download
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for downloading the object
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            current_app.logger.error(f"Error generating presigned URL: {str(e)}")
            raise
    
    def delete_file(self, bucket_name: str, object_key: str) -> bool:
        """
        Delete a file from R2 storage.
        
        Args:
            bucket_name: The bucket containing the object
            object_key: The key of the object to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_object(
                Bucket=bucket_name,
                Key=object_key
            )
            return True
        except ClientError as e:
            current_app.logger.error(f"Error deleting object from R2: {str(e)}")
            return False


# Create a singleton instance
cloud_storage = CloudStorageService() 