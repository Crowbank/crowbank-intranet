from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import date

from .base import Base

class DailyAllocation(Base):
    """
    Represents the allocation of a pet from a booking to a specific boarding run for a specific day.
    This allows tracking which run a pet is assigned to on each day of their stay.
    
    Note: Even though bookings can have multiple pets, each DailyAllocation refers to 
    a specific pet-booking-run combination for a single day.
    """
    __tablename__ = 'daily_allocations'

    id = Column(Integer, primary_key=True)
    allocation_date = Column(Date, nullable=False)
    
    # Foreign Keys
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    boarding_run_id = Column(Integer, ForeignKey('boarding_runs.id'), nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="daily_allocations")
    pet = relationship("Pet", back_populates="daily_allocations")
    boarding_run = relationship("BoardingRun", back_populates="daily_allocations")
    
    def __repr__(self):
        return f"<DailyAllocation(id={self.id}, date='{self.allocation_date}', booking_id={self.booking_id}, pet_id={self.pet_id}, run_id={self.boarding_run_id})>" 