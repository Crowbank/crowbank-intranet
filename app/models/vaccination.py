from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Interval, Boolean
from sqlalchemy.orm import relationship

from .base import Base

class Vaccination(Base):
    __tablename__ = 'vaccinations'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    validity_period = Column(Interval, nullable=True)  # How long the vaccination is valid for
    
    # Foreign Keys
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    
    # Relationships
    species = relationship("Species", back_populates="vaccinations")
    events = relationship("VaccinationEvent", back_populates="vaccination")
    
    def __repr__(self):
        return f"<Vaccination(id={self.id}, name='{self.name}')>"

class VaccinationEvent(Base):
    __tablename__ = 'vaccination_events'

    id = Column(Integer, primary_key=True)
    date_administered = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    confirmed = Column(Boolean, default=False, nullable=False)  # Flag to indicate if event is confirmed by staff
    
    # Foreign Keys
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    vaccination_id = Column(Integer, ForeignKey('vaccinations.id'), nullable=False)
    administered_by_id = Column(Integer, ForeignKey('vets.id'), nullable=True)
    
    # Relationships
    pet = relationship("Pet", back_populates="vaccination_events")
    vaccination = relationship("Vaccination", back_populates="events")
    administered_by = relationship("Vet")
    
    def __repr__(self):
        return f"<VaccinationEvent(id={self.id}, pet_id={self.pet_id}, vaccination_id={self.vaccination_id}, date={self.date_administered}, confirmed={self.confirmed})>" 