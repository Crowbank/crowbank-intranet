"""
Pet Document Service

This service manages the creation, storage, and retrieval of pet documents in cloud storage.
"""

from typing import BinaryIO, Dict, List, Optional, Union
from datetime import datetime
from werkzeug.datastructures import FileStorage
from sqlalchemy.orm import Session

from app.models import PetDocument, Pet, DocumentType
from app.utils.cloud_storage import cloud_storage
from flask import current_app

class PetDocumentService:
    """Service for managing pet documents."""
    
    @staticmethod
    def upload_document(
        db_session: Session,
        pet_id: int,
        file: FileStorage,
        title: str,
        document_type: str,
        notes: Optional[str] = None,
        bucket_name: Optional[str] = None
    ) -> PetDocument:
        """
        Upload a pet document to cloud storage and save metadata in the database.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet this document belongs to
            file: Uploaded file object
            title: Document title
            document_type: Type of document (from DocumentType enum)
            notes: Optional notes about the document
            bucket_name: Override the default bucket name
            
        Returns:
            The created PetDocument instance
        """
        if bucket_name is None:
            # First check environment-specific config if available
            env = current_app.config.get('ENV', 'dev')  # Using shortened env name (dev/prod/test)
            
            # Access the storage configuration structure
            # The flattened config would have STORAGE_BUCKETS_PET_DOCUMENTS_<ENV>
            bucket_name = current_app.config.get(f'STORAGE_BUCKETS_PET_DOCUMENTS_{env.upper()}')
            
            # Fall back to default bucket if env-specific not found
            if not bucket_name:
                bucket_name = current_app.config.get('STORAGE_DEFAULT_DOCUMENT_BUCKET')
                
            # If still no bucket name, check the nested config structure
            if not bucket_name and 'CONFIG' in current_app.config:
                nested_config = current_app.config['CONFIG']
                bucket_name = nested_config.get('storage', {}).get('buckets', {}).get(
                    'pet_documents', {}).get(env)
                
                if not bucket_name:
                    bucket_name = nested_config.get('storage', {}).get('default_document_bucket')
                
            # If still no bucket name, raise an error
            if not bucket_name:
                current_app.logger.error("No document bucket configured")
                raise ValueError("Cloud storage bucket not configured. Check application configuration.")
        
        # Use the pet ID as part of the storage path
        prefix = f"pets/{pet_id}"
        
        # Upload to cloud storage
        metadata = cloud_storage.upload_file(
            file_obj=file.stream,
            original_filename=file.filename,
            bucket_name=bucket_name,
            content_type=file.content_type,
            prefix=prefix
        )
        
        # Create document record
        document = PetDocument(
            pet_id=pet_id,
            title=title,
            type=document_type,
            original_filename=metadata['original_filename'],
            object_key=metadata['object_key'],
            bucket_name=metadata['bucket_name'],
            content_type=metadata['content_type'],
            file_size=metadata['file_size'],
            upload_date=datetime.utcnow(),
            last_modified=metadata.get('last_modified'),
            notes=notes
        )
        
        # Save to database
        db_session.add(document)
        db_session.commit()
        
        return document
    
    @staticmethod
    def upload_vaccination_document(
        db_session: Session,
        pet_id: int,
        file: FileStorage,
        title: str = "Vaccination Card",
        notes: Optional[str] = None,
        set_as_primary: bool = True,
        bucket_name: Optional[str] = None
    ) -> PetDocument:
        """
        Upload a vaccination document for a pet and optionally set it as their primary vaccination card.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet this document belongs to
            file: Uploaded file object
            title: Document title (defaults to "Vaccination Card")
            notes: Optional notes about the document
            set_as_primary: Whether to set this as the pet's primary vaccination card
            bucket_name: Override the default bucket name
            
        Returns:
            The created PetDocument instance
        """
        # Upload using the standard method with vaccination type
        document = PetDocumentService.upload_document(
            db_session=db_session,
            pet_id=pet_id,
            file=file,
            title=title,
            document_type=DocumentType.VACCINATION,
            notes=notes,
            bucket_name=bucket_name
        )
        
        # Set as the pet's primary vaccination card if requested
        if set_as_primary:
            pet = db_session.query(Pet).get(pet_id)
            if pet:
                pet.vaccination_document_id = document.id
                db_session.commit()
        
        return document
    
    @staticmethod
    def get_documents_for_pet(db_session: Session, pet_id: int) -> List[PetDocument]:
        """
        Get all documents for a specific pet.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet
            
        Returns:
            List of PetDocument instances
        """
        return db_session.query(PetDocument).filter(PetDocument.pet_id == pet_id).all()
    
    @staticmethod
    def get_documents_by_type(db_session: Session, pet_id: int, document_type: DocumentType) -> List[PetDocument]:
        """
        Get all documents of a specific type for a pet.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet
            document_type: Type of document to retrieve
            
        Returns:
            List of PetDocument instances
        """
        return db_session.query(PetDocument).filter(
            PetDocument.pet_id == pet_id,
            PetDocument.type == document_type
        ).all()
    
    @staticmethod
    def get_vaccination_document(db_session: Session, pet_id: int) -> Optional[PetDocument]:
        """
        Get the primary vaccination document for a pet.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet
            
        Returns:
            The primary vaccination PetDocument or None if not found
        """
        pet = db_session.query(Pet).get(pet_id)
        if not pet:
            return None
            
        return pet.vaccination_card
    
    @staticmethod
    def set_vaccination_document(db_session: Session, pet_id: int, document_id: int) -> bool:
        """
        Set a specific document as the pet's vaccination card.
        
        Args:
            db_session: SQLAlchemy database session
            pet_id: ID of the pet
            document_id: ID of the document to set as vaccination card
            
        Returns:
            True if successful, False otherwise
        """
        pet = db_session.query(Pet).get(pet_id)
        document = db_session.query(PetDocument).get(document_id)
        
        if not pet or not document:
            return False
            
        # Ensure the document belongs to this pet and is a vaccination type
        if document.pet_id != pet_id or document.type != DocumentType.VACCINATION:
            return False
            
        pet.vaccination_document_id = document_id
        db_session.commit()
        return True
    
    @staticmethod
    def get_document_download_url(document: PetDocument, expires_in: int = 3600) -> str:
        """
        Generate a temporary download URL for a document.
        
        Args:
            document: The PetDocument instance
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL for downloading the document
        """
        return cloud_storage.get_download_url(
            bucket_name=document.bucket_name,
            object_key=document.object_key,
            expires_in=expires_in
        )
    
    @staticmethod
    def delete_document(db_session: Session, document_id: int) -> bool:
        """
        Delete a document from cloud storage and database.
        
        Args:
            db_session: SQLAlchemy database session
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        document = db_session.query(PetDocument).get(document_id)
        
        if document is None:
            return False
        
        # If this is a pet's vaccination document, unset that relationship
        for pet in document.vaccination_for_pets:
            pet.vaccination_document_id = None
        
        # Delete from cloud storage
        success = cloud_storage.delete_file(
            bucket_name=document.bucket_name,
            object_key=document.object_key
        )
        
        if success:
            # Remove from database
            db_session.delete(document)
            db_session.commit()
            
        return success 