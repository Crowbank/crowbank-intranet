from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Species(Base):
    __tablename__ = 'species'

    id = Column(Integer, primary_key=True)
    legacy_spec_no = Column(Integer, nullable=True, unique=True)
    name = Column(String(50), nullable=False, unique=True)  # 'Dog', 'Cat', etc.
    
    # Relationships
    breeds = relationship("Breed", back_populates="species")
    pets = relationship("Pet", back_populates="species")
    vaccinations = relationship("Vaccination", back_populates="species")
    
    def __repr__(self):
        return f"<Species(id={self.id}, name='{self.name}')>" 