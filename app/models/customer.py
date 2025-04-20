import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import Base
from .vet import Vet

# Enum for Contact Roles
class ContactRole(str, enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    EMERGENCY = "emergency"

# Association Table for Customer-Contact Many-to-Many
class CustomerContact(Base):
    __tablename__ = 'customer_contacts' # Changed to plural snake_case

    customer_id = Column(Integer, ForeignKey('customers.id'), primary_key=True) # FK to customers.id
    contact_id = Column(Integer, ForeignKey('contacts.id'), primary_key=True) # FK to contacts.id
    role = Column(Enum(ContactRole), nullable=False)

    # Relationships to easily access Customer and Contact from the association object
    customer = relationship("Customer", back_populates="contact_associations")
    contact = relationship("Contact", back_populates="customer_associations")

# Contact Model (Individual Person)
class Contact(Base):
    __tablename__ = 'contacts' # Changed to plural snake_case

    id = Column(Integer, primary_key=True) # Changed PK to id
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=True)
    email_address = Column(String(255), nullable=True, unique=True)
    notes = Column(Text, nullable=True)

    # Relationship to the association table
    customer_associations = relationship("CustomerContact", back_populates="contact")

    def __repr__(self):
        return f"<Contact(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"

# Customer Model (Household)
class Customer(Base):
    __tablename__ = 'customers' # Changed to plural snake_case

    id = Column(Integer, primary_key=True) # Changed PK to id
    legacy_cust_no = Column(Integer, nullable=True, unique=True) # Added legacy ID field

    # Address fields (using 'street' as per canvas example)
    street = Column(String(255), nullable=True) # Renamed address_line_1 to street
    address_line_2 = Column(String(255), nullable=True)
    town = Column(String(100), nullable=True) # Renamed town_city to town
    county = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)

    # Default Vet (FK - linking to Vet model)
    default_vet_id = Column(Integer, ForeignKey('vets.id'), nullable=True) # Uncommented and confirmed FK
    default_vet = relationship("Vet") # Uncommented relationship, added backref placeholder if needed later

    # Relationship to the association table
    contact_associations = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")

    # Convenience properties to get contacts by role (optional but useful)
    @property
    def primary_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.PRIMARY]

    @property
    def secondary_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.SECONDARY]

    @property
    def emergency_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.EMERGENCY]

    # Assuming Pet model relationship might still be relevant at the Customer (household) level
    # pets = relationship("Pet", back_populates="customer") # Changed from owner to customer

    def __repr__(self):
        # Maybe represent customer by primary contact's name or legacy ID if available
        primary = self.primary_contacts
        name = f"{primary[0].first_name} {primary[0].last_name}" if primary else f"Household {self.id}"
        return f"<Customer(id={self.id}, name='{name}', legacy_cust_no={self.legacy_cust_no})>" 