from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

from .base import Base

# Association table for many-to-many relationship between pets and medical conditions
pet_condition_association = Table(
    'pet_condition_association',
    Base.metadata,
    Column('pet_id', Integer, ForeignKey('pets.id'), primary_key=True),
    Column('condition_id', Integer, ForeignKey('medical_conditions.id'), primary_key=True)
)

class MedicalCondition(Base):
    """Model for medical conditions (e.g., diabetic, epileptic, blind, deaf)."""
    __tablename__ = 'medical_conditions'

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships - many-to-many with pets
    pets = relationship("Pet", secondary=pet_condition_association, back_populates="medical_conditions")
    
    def __repr__(self):
        return f"<MedicalCondition(id={self.id}, name='{self.name}')>" 