"""
Models package for Crowbank Intranet.

This package contains SQLAlchemy ORM models for the Crowbank Intranet system.
All models are imported here for easy access.
"""

from .base import Base
from .boarding_run import BoardingRun
from .booking import BoardingType, Booking, BookingStatus

# Import all models here to ensure they are registered with the Base
from .breed import Breed, BreedCategory
from .customer import Customer
from .daily_allocation import DailyAllocation
from .employee import Employee
from .form import (
    EntityType,
    FieldType,
    FormField,
    FormFile,
    FormResponse,
    FormSubmission,
    FormTemplate,
    FormType,
)
from .insurance import Insurance
from .media_file import MediaFile, MediaType, pet_media_association
from .medical_condition import MedicalCondition, pet_condition_association
from .pet import Pet
from .pet_document import DocumentType, PetDocument
from .pet_weight import PetWeight
from .species import Species
from .vaccination import Vaccination, VaccinationEvent
from .vet import Vet

__all__ = [
    "Base",
    "BoardingRun",
    "BoardingType",
    "Booking",
    "BookingStatus",
    "Breed",
    "BreedCategory",
    "Contact",
    "ContactRole",
    "Customer",
    "CustomerContact",
    "DailyAllocation",
    "DocumentType",
    "Employee",
    "EntityType",
    "FieldType",
    "FormField",
    "FormFile",
    "FormResponse",
    "FormSubmission",
    "FormTemplate",
    "FormType",
    "Insurance",
    "MediaFile",
    "MediaType",
    "MedicalCondition",
    "Pet",
    "PetDocument",
    "PetWeight",
    "Species",
    "Vaccination",
    "VaccinationEvent",
    "Vet",
]
