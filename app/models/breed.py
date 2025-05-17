from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Numeric
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
    
    # Additional legacy attributes
    suspect = Column(Boolean, default=False, nullable=False)
    weight = Column(Numeric(5, 2), nullable=True)  # 1=small, 2=medium, 3=large
    share_single = Column(Boolean, default=True, nullable=False)
    
    # Foreign Keys
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('breed_categories.id'), nullable=True)
    
    # Relationships
    species = relationship("Species", back_populates="breeds")
    category = relationship("BreedCategory", back_populates="breeds")
    pets = relationship("Pet", back_populates="breed")
    
    def __repr__(self):
        return f"<Breed(id={self.id}, name='{self.name}')>" 