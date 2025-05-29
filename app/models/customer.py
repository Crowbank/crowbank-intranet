import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, Numeric
from sqlalchemy.orm import relationship

from .base import Base
from .vet import Vet
from .mixins import AddressMixin

# Enum for Contact Roles
class ContactRole(str, enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    EMERGENCY = "emergency"

# Association Table for Customer-Contact Many-to-Many
class CustomerContact(Base):
    __tablename__ = 'customer_contacts'

    customer_id = Column(Integer, ForeignKey('customers.id'), primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), primary_key=True)
    role = Column(Enum(ContactRole), nullable=False)

    customer = relationship("Customer", back_populates="contact_associations")
    contact = relationship("Contact", back_populates="customer_associations")

# Contact Model (Individual Person)
class Contact(Base, AddressMixin):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=True)
    email_address = Column(String(255), nullable=True, unique=True)
    notes = Column(Text, nullable=True)

    customer_associations = relationship("CustomerContact", back_populates="contact")

    def __repr__(self):
        return f"<Contact(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"

# Customer Model (Household)
class Customer(Base, AddressMixin):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    legacy_cust_no = Column(Integer, nullable=True, unique=True)

    # Updated fields
    notes = Column(Text, nullable=True)
    banned = Column(Boolean, nullable=False, default=False)
    opt_out = Column(Boolean, nullable=False, default=False)
    discount = Column(Numeric(5, 2), nullable=False, default=0)

    # Default Vet (FK - linking to Vet model)
    default_vet_id = Column(Integer, ForeignKey('vets.id'), nullable=True)
    default_vet = relationship(Vet, back_populates="customers")

    # Relationship to the association table
    contact_associations = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")

    @property
    def primary_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.PRIMARY]

    @property
    def secondary_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.SECONDARY]

    @property
    def emergency_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.EMERGENCY]

    def __repr__(self):
        primary = self.primary_contacts
        name = f"{primary[0].first_name} {primary[0].last_name}" if primary else f"Household {self.id}"
        return f"<Customer(id={self.id}, name='{name}', legacy_cust_no={self.legacy_cust_no})>"
