from sqlalchemy import Column, Integer, Float, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import date

from .base import Base

class PetWeight(Base):
    __tablename__ = 'pet_weights'

    id = Column(Integer, primary_key=True)
    weight = Column(Float, nullable=False)  # Weight in kg
    date_recorded = Column(Date, default=date.today, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Foreign Keys
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    recorded_by = Column(Integer, ForeignKey('employees.id'), nullable=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="weights")
    recorded_by_employee = relationship("Employee", back_populates="pet_weights_recorded")
    
    def __repr__(self):
        return f"<PetWeight(id={self.id}, pet_id={self.pet_id}, weight={self.weight}, date={self.date_recorded})>" 