import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship, validates

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

    # Add validation to ensure a contact can only be PRIMARY for one customer
    @validates('role')
    def validate_primary_role(self, key, role):
        if role == ContactRole.PRIMARY:
            # Check if this contact is already PRIMARY for another customer
            existing = self.contact.primary_customer if self.contact else None
            if existing and existing.id != self.customer_id:
                raise ValueError(f"Contact is already a PRIMARY contact for customer {existing.id}")
        return role

    __table_args__ = (
        # This ensures a contact can only have one role per customer
        UniqueConstraint('customer_id', 'contact_id', name='uix_customer_contact'),
    )

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

    @property
    def primary_customer(self):
        """Get the customer for which this contact is the PRIMARY contact."""
        for assoc in self.customer_associations:
            if assoc.role == ContactRole.PRIMARY:
                return assoc.customer
        return None

    @property
    def secondary_customers(self):
        """Get all customers for which this contact is a SECONDARY contact."""
        return [assoc.customer for assoc in self.customer_associations 
                if assoc.role == ContactRole.SECONDARY]

    @property
    def emergency_customers(self):
        """Get all customers for which this contact is an EMERGENCY contact."""
        return [assoc.customer for assoc in self.customer_associations 
                if assoc.role == ContactRole.EMERGENCY]
    
    @property
    def full_name(self):
        """Get the full name of the contact."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.full_name}')>"
    e
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

    # Stripe customer id (optional)
    stripe_id = Column(String(50), nullable=True, unique=True)

    # Default Vet (FK - linking to Vet model)
    default_vet_id = Column(Integer, ForeignKey('vets.id'), nullable=True)
    default_vet = relationship(Vet, back_populates="customers")

    # Relationship to the association table
    contact_associations = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
    
    # Relationship to pets
    pets = relationship("Pet", back_populates="owner")
    
    # Relationship to bookings
    bookings = relationship("Booking", back_populates="customer")
    
    # Relationship to form submissions
    form_submissions = relationship("FormSubmission", foreign_keys="FormSubmission.customer_id", back_populates="customer")

    @property
    def primary_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.PRIMARY]

    @property
    def primary_contact(self):
        """Get the first primary contact for this customer, or None if none exists."""
        contacts = self.primary_contacts
        return contacts[0] if contacts else None

    @property
    def secondary_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.SECONDARY]

    @property
    def emergency_contacts(self):
        return [assoc.contact for assoc in self.contact_associations if assoc.role == ContactRole.EMERGENCY]
        
    @property
    def display_name(self):
        """Return a display name for the customer based on primary contact."""
        if self.primary_contact:
            return f"{self.primary_contact.full_name}'s Household"
        return f"Household {self.id}"

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.display_name}', legacy_cust_no={self.legacy_cust_no})>"
        
    def get_form_submissions(self, form_type=None):
        """
        Get form submissions for this customer, optionally filtered by form type.
        
        Args:
            form_type: Optional FormType enum value to filter by
            
        Returns:
            List of FormSubmission instances
        """
        if form_type:
            return [s for s in self.form_submissions if s.template.type == form_type]
        return self.form_submissions 