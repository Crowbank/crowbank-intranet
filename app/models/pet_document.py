import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class DocumentType(str, enum.Enum):
    VACCINATION = "vaccination"
    INSTRUCTIONS = "instructions"
    MEDICATION_SHEET = "medication_sheet"
    VET_VISIT_SHEET = "vet_visit_sheet"
    OTHER = "other"

class PetDocument(Base):
    __tablename__ = 'pet_documents'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=True)
    type = Column(Enum(DocumentType), nullable=False, default=DocumentType.OTHER)
    
    # Original filename provided by the user during upload
    original_filename = Column(String(255), nullable=True)
    
    # Cloud storage metadata
    object_key = Column(String(255), nullable=True)  # Unique identifier in cloud storage (R2)
    bucket_name = Column(String(100), nullable=True)  # R2 bucket name
    content_type = Column(String(100), nullable=True)  # MIME type
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Storage access info
    public_url = Column(String(1000), nullable=True)  # Optional public URL if document is public
    
    # Timestamps
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_modified = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Foreign Keys
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="documents", foreign_keys=[pet_id])
    
    # Pets that use this document as their vaccination card
    vaccination_for_pets = relationship("Pet", 
                                      foreign_keys="Pet.vaccination_document_id", 
                                      back_populates="vaccination_document")
    
    def __repr__(self):
        return f"<PetDocument(id={self.id}, title='{self.title}', type='{self.type}')>"
    
    @property
    def download_url(self):
        """Get a download URL for this document (to be implemented by a service)"""
        # This would typically call the cloud storage service to generate a URL
        # return pet_document_service.get_document_download_url(self)
        return None 