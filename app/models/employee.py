from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date

from .base import Base
from app.utils.age_util import calculate_age, format_age

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True, unique=True)
    phone = Column(String(20), nullable=True)
    position = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    hire_date = Column(Date, nullable=True)
    date_of_birth = Column(Date, nullable=True)  # Added for age calculation
    notes = Column(Text, nullable=True)
    
    # Relationships
    pet_weights_recorded = relationship("PetWeight", back_populates="recorded_by_employee")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.first_name} {self.last_name}')>"
    
    @property
    def full_name(self):
        """Return the employee's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate the age of the employee based on date of birth."""
        return calculate_age(self.date_of_birth)
    
    def age_str(self):
        """Return the employee's age as a formatted string (e.g., '32y 3m')."""
        return format_age(self.age) 