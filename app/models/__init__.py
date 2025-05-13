"""
Models package for Crowbank Intranet.

This package contains SQLAlchemy ORM models for the Crowbank Intranet system.
All models are imported here for easy access.
"""

from .base import Base
# Import all models here to ensure they are registered with the Base
from .breed import Breed, BreedCategory
from .booking import Booking, BookingStatus, BoardingType
from .boarding_run import BoardingRun
from .customer import Customer
from .daily_allocation import DailyAllocation
from .employee import Employee
from .form import FormTemplate, FormField, FormSubmission, FormResponse, FormFile
from .form import FormType, EntityType, FieldType
from .insurance import Insurance
from .media_file import MediaFile, MediaType, pet_media_association
from .medical_condition import MedicalCondition, pet_condition_association
from .pet import Pet
from .pet_document import PetDocument, DocumentType
from .pet_weight import PetWeight
from .species import Species
from .vaccination import Vaccination, VaccinationEvent
from .vet import Vet

__all__ = [
    'Base',
    'Customer',
    'Contact', 
    'CustomerContact',
    'ContactRole',
    'Vet',
    'Species',
    'Breed',
    'BreedCategory',
    'Pet',
    'Vaccination',
    'VaccinationEvent',
    'PetDocument',
    'DocumentType',
    'PetWeight',
    'BoardingRun',
    'BoardingType',
    'Booking',
    'BookingStatus',
    'Employee',
    'DailyAllocation',
    'MediaFile',
    'MediaType',
    'Insurance',
    'MedicalCondition',
    'FormTemplate',
    'FormField',
    'FormSubmission',
    'FormResponse',
    'FormFile',
    'FormType',
    'EntityType',
    'FieldType',
] 