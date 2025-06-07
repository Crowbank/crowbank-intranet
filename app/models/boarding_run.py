import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from .base import Base
from .species import Species

class RunType(Base):
    __tablename__ = 'run_types'

    id = Column(Integer, primary_key=True)
    description = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)

    species = relationship('Species')
    boarding_runs = relationship('BoardingRun', back_populates='run_type')

    def __repr__(self):
        return f"<RunType(id={self.id}, code='{self.code}', description='{self.description}', capacity={self.capacity})>"

class BoardingRun(Base):
    __tablename__ = 'boarding_runs'

    id = Column(Integer, primary_key=True)
    # Legacy primary key from PetAdmin
    legacy_run_no = Column(Integer, nullable=True, unique=True)
    name = Column(String(50), nullable=False)  # e.g., "North F1"
    code = Column(String(10), nullable=False)  # e.g., "NF1"
    wing = Column(String(50), nullable=True)  # e.g., "North", "South"
    side = Column(String(50), nullable=True)  # e.g., "Front", "Back"
    is_active = Column(Boolean, nullable=False, default=True)
    run_type_id = Column(Integer, ForeignKey('run_types.id'), nullable=False)

    # Relationships
    run_type = relationship('RunType', back_populates='boarding_runs')
    bookings = relationship("Booking", back_populates="assigned_run")
    daily_allocations = relationship("DailyAllocation", back_populates="boarding_run")

    def __repr__(self):
        return f"<BoardingRun(id={self.id}, name='{self.name}', run_type_id={self.run_type_id})>" 