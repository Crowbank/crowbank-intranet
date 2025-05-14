from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

from .models.base import Base
from .models.customer import Customer, Contact, CustomerContact, ContactRole
from .models.vet import Vet
from .models.species import Species
from .models.breed import Breed, BreedCategory
from .models.pet import Pet
from .models.vaccination import Vaccination, VaccinationEvent
from .models.pet_document import PetDocument, DocumentType
from .models.pet_weight import PetWeight
from .models.boarding_run import BoardingRun, BoardingType
from .models.booking import Booking, BookingStatus

# Get database password from environment or use default
db_password = os.getenv('DB_PASSWORD', 'ZhV8Pk521j1Z')

# Create engine
engine = create_engine(f'postgresql://crowbank:{db_password}@localhost/crowbank')

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session."""
    return Session() 