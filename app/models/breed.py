from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class BreedCategory(Base):
    __tablename__ = 'breed_categories'

    id = Column(Integer, primary_key=True)
    legacy_breedcat_no = Column(Integer, nullable=True, unique=True)
    name = Column(String(50), nullable=False)  # 'Small', 'Medium', 'Large', etc.
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    
    # Relationships
    species = relationship("Species")
    breeds = relationship("Breed", back_populates="category")
    
    def __repr__(self):
        return f"<BreedCategory(id={self.id}, name='{self.name}')>"

class Breed(Base):
    __tablename__ = 'breeds'

    id = Column(Integer, primary_key=True)
    legacy_breed_no = Column(Integer, nullable=True, unique=True)
    name = Column(String(100), nullable=False)
    short_name = Column(String(30), nullable=True)  # Abbreviated name, e.g., "GSD" for "German Shepherd Dog"
    
    # Foreign Keys
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('breed_categories.id'), nullable=True)
    
    # Relationships
    species = relationship("Species", back_populates="breeds")
    category = relationship("BreedCategory", back_populates="breeds")
    pets = relationship("Pet", back_populates="breed")
    
    def __repr__(self):
        return f"<Breed(id={self.id}, name='{self.name}')>" 