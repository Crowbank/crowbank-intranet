import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"

# Association table for many-to-many relationship between pets and media files
pet_media_association = Table(
    'pet_media_association',
    Base.metadata,
    Column('pet_id', Integer, ForeignKey('pets.id'), primary_key=True),
    Column('media_id', Integer, ForeignKey('media_files.id'), primary_key=True)
)

class MediaFile(Base):
    """Model for media files (photos and videos) that can be tagged with multiple pets."""
    __tablename__ = 'media_files'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(MediaType), nullable=False)
    
    # Cloud storage metadata
    original_filename = Column(String(255), nullable=True)
    object_key = Column(String(255), nullable=False)  # Unique identifier in cloud storage
    bucket_name = Column(String(100), nullable=False)
    content_type = Column(String(100), nullable=True)  # MIME type
    file_size = Column(Integer, nullable=True)  # Size in bytes
    
    # Thumbnail info (for faster loading in UI)
    thumbnail_key = Column(String(255), nullable=True)
    
    # Media metadata
    width = Column(Integer, nullable=True)  # For images/videos
    height = Column(Integer, nullable=True)  # For images/videos
    duration = Column(Integer, nullable=True)  # Duration in seconds for videos
    
    # Storage access info
    public_url = Column(String(1000), nullable=True)  # Optional public URL if media is public
    
    # Timestamps
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    capture_date = Column(DateTime, nullable=True)  # When the photo/video was taken
    
    # Relationships - many-to-many with pets
    pets = relationship("Pet", secondary=pet_media_association, back_populates="media_files")
    
    def __repr__(self):
        return f"<MediaFile(id={self.id}, type='{self.type}', title='{self.title}')>" 