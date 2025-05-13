from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import date

from .base import Base
from .media_file import pet_media_association
from .medical_condition import pet_condition_association
from .pet_document import DocumentType
from app.utils.age_util import calculate_age, format_age

class Pet(Base):
    __tablename__ = 'pets'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    sex = Column(String(1), nullable=True)  # M/F
    neutered = Column(Boolean, default=False, nullable=False)
    microchip = Column(String(30), nullable=True)
    deceased = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Warning flag and text for pets that need special attention
    warning = Column(Text, nullable=True)
    
    # Special needs and behavior notes
    feeding_notes = Column(Text, nullable=True)
    medical_notes = Column(Text, nullable=True)
    behavior_notes = Column(Text, nullable=True)
    
    # Boarding and daycare related flags
    friends_allowed = Column(Boolean, default=True, nullable=False)  # Can interact with other pets
    daycare_approved = Column(Boolean, default=False, nullable=False)  # Approved for daycare service
    distinguishing_marks = Column(Text, nullable=True)  # Identifying marks or features
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    breed_id = Column(Integer, ForeignKey('breeds.id'), nullable=True)
    vet_id = Column(Integer, ForeignKey('vets.id'), nullable=True)
    insurance_id = Column(Integer, ForeignKey('insurance.id'), nullable=True)
    primary_photo_id = Column(Integer, ForeignKey('media_files.id'), nullable=True)
    vaccination_document_id = Column(Integer, ForeignKey('pet_documents.id'), nullable=True)
    
    # Relationships
    owner = relationship("Customer", back_populates="pets")
    species = relationship("Species", back_populates="pets")
    breed = relationship("Breed", back_populates="pets")
    default_vet = relationship("Vet", back_populates="pets")
    # Updated relationship to use the BookingPet association model
    booking_details = relationship("BookingPet", back_populates="pet")
    bookings = relationship("Booking", secondary="booking_pets", viewonly=True)
    booking_intents = relationship("BookingIntent", secondary="booking_intent_pets", back_populates="pets")
    vaccination_events = relationship("VaccinationEvent", back_populates="pet")
    documents = relationship("PetDocument", back_populates="pet", foreign_keys="PetDocument.pet_id")
    weights = relationship("PetWeight", back_populates="pet")
    daily_allocations = relationship("DailyAllocation", back_populates="pet")
    vet = relationship("Vet", back_populates="pets")
    insurance = relationship("Insurance", back_populates="pets")
    primary_photo = relationship("MediaFile", foreign_keys=[primary_photo_id])
    vaccination_document = relationship("PetDocument", foreign_keys=[vaccination_document_id])
    form_submissions = relationship("FormSubmission", foreign_keys="FormSubmission.pet_id", back_populates="pet")
    
    # Many-to-many relationship with media files
    media_files = relationship("MediaFile", secondary=pet_media_association, back_populates="pets")
    
    # Many-to-many relationship with medical conditions
    medical_conditions = relationship("MedicalCondition", secondary=pet_condition_association, back_populates="pets")
    
    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', species='{self.species.name if self.species else 'Unknown'}')>"
    
    @property
    def current_weight(self):
        """Get the most recent weight of the pet in kg."""
        if not self.weights:
            return None
            
        # Get the most recent weight entry
        latest_weight = sorted(self.weights, key=lambda w: w.date_recorded, reverse=True)[0]
        return latest_weight.weight
    
    @property
    def age(self):
        """Calculate the age of the pet based on date of birth."""
        return calculate_age(self.date_of_birth)
    
    def age_str(self):
        """Return the pet's age as a formatted string (e.g., '3y 4m')."""
        return format_age(self.age)
    
    def get_booking_details(self, booking_id):
        """
        Get specific details for this pet in a particular booking.
        
        Args:
            booking_id: ID of the booking to get details for
            
        Returns:
            BookingPet instance or None if not in that booking
        """
        for booking_detail in self.booking_details:
            if booking_detail.booking_id == booking_id:
                return booking_detail
        return None
    
    def get_form_submissions(self, form_type=None):
        """
        Get form submissions for this pet, optionally filtered by form type.
        
        Args:
            form_type: Optional FormType enum value to filter by
            
        Returns:
            List of FormSubmission instances
        """
        if form_type:
            return [s for s in self.form_submissions if s.template.type == form_type]
        return self.form_submissions
    
    def has_completed_form(self, form_type):
        """
        Check if this pet has a completed form of the specified type.
        
        Args:
            form_type: FormType enum value to check for
            
        Returns:
            Boolean indicating if a completed form exists
        """
        return any(s.is_complete and s.template.type == form_type for s in self.form_submissions)
    
    def get_documents_by_type(self, document_type):
        """
        Get all documents of a specific type for this pet.
        
        Args:
            document_type: DocumentType enum value
            
        Returns:
            List of PetDocument instances of the specified type
        """
        return [doc for doc in self.documents if doc.type == document_type]
    
    @property
    def vaccination_card(self):
        """
        Get the vaccination card document for this pet.
        
        Returns:
            The specific vaccination document if set, otherwise tries to find one
            from the pet's documents with type=VACCINATION
        """
        # First try the direct relationship if set
        if self.vaccination_document:
            return self.vaccination_document
            
        # Otherwise, look for the first vaccination document in all documents
        vaccination_docs = self.get_documents_by_type(DocumentType.VACCINATION)
        return vaccination_docs[0] if vaccination_docs else None
    
    def set_vaccination_card(self, document):
        """
        Set the specific vaccination card document for this pet.
        
        Args:
            document: PetDocument instance to set as the vaccination document
            
        Raises:
            ValueError: If document is not a vaccination type document
        """
        if document.type != DocumentType.VACCINATION:
            raise ValueError("Document must be of type VACCINATION to be set as vaccination card")
            
        self.vaccination_document_id = document.id 