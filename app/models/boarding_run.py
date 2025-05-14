import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from .base import Base

class BoardingType(str, enum.Enum):
    DOG_STANDARD = "dog_standard"
    DOG_DELUXE = "dog_deluxe"
    DOG_DOUBLE = "dog_double"
    CATTERY = "cattery"

class BoardingRun(Base):
    __tablename__ = 'boarding_runs'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # e.g., "North F1"
    code = Column(String(10), nullable=False)  # e.g., "NF1"
    wing = Column(String(50), nullable=True)  # e.g., "North", "South"
    side = Column(String(50), nullable=True)  # e.g., "Front", "Back"
    type = Column(Enum(BoardingType), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    
    # Relationships
    bookings = relationship("Booking", back_populates="assigned_run")
    daily_allocations = relationship("DailyAllocation", back_populates="boarding_run")
    
    def __repr__(self):
        return f"<BoardingRun(id={self.id}, name='{self.name}', type='{self.type}')>" 