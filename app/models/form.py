import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime, JSON, Boolean, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class FormType(str, enum.Enum):
    """Types of forms in the system"""
    NEW_DOG_QUESTIONNAIRE = "new_dog_questionnaire"
    DAYCARE_APPLICATION = "daycare_application"
    PUPPY_CLASS_REGISTRATION = "puppy_class_registration"
    CHECKIN_FORM = "checkin_form"
    BOOKING_INTENT = "booking_intent"
    EMPLOYEE_STARTER = "employee_starter"
    # Add more as needed

class EntityType(str, enum.Enum):
    """Types of entities that forms can be associated with"""
    PET = "pet"
    BOOKING = "booking"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    # Add more as needed

class FieldType(str, enum.Enum):
    """Types of fields that can be in forms"""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    # Add more as needed

class FormTemplate(Base):
    """Template that defines a form's structure"""
    __tablename__ = 'form_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(FormType), nullable=False)
    entity_type = Column(Enum(EntityType), nullable=False)  # What this form relates to (pet, booking, etc.)
    gravity_form_id = Column(Integer, nullable=True)  # ID of the corresponding Gravity Form
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)  # Form version for tracking changes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    fields = relationship("FormField", back_populates="template", cascade="all, delete-orphan")
    submissions = relationship("FormSubmission", back_populates="template")
    
    def __repr__(self):
        return f"<FormTemplate(id={self.id}, name='{self.name}', type='{self.type}')>"

class FormField(Base):
    """Field within a form template"""
    __tablename__ = 'form_fields'

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    field_key = Column(String(50), nullable=False)  # Machine-readable key (e.g., "pet_name")
    label = Column(String(255), nullable=False)  # Human-readable label (e.g., "Pet's Name")
    field_type = Column(Enum(FieldType), nullable=False)
    required = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)  # Display order in form
    options = Column(JSON, nullable=True)  # For select/multiselect/radio/checkbox options
    default_value = Column(Text, nullable=True)
    help_text = Column(Text, nullable=True)
    gravity_field_id = Column(Integer, nullable=True)  # ID in the Gravity Forms system
    
    # Relationships
    template = relationship("FormTemplate", back_populates="fields")
    responses = relationship("FormResponse", back_populates="field")
    
    # Ensure field_key is unique within a template
    __table_args__ = (
        UniqueConstraint('template_id', 'field_key', name='uix_template_field_key'),
    )
    
    def __repr__(self):
        return f"<FormField(id={self.id}, key='{self.field_key}', type='{self.field_type}')>"

class FormSubmission(Base):
    """A single submission of a form"""
    __tablename__ = 'form_submissions'

    id = Column(Integer, primary_key=True)
    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False)
    
    # Polymorphic association to different entity types
    entity_type = Column(Enum(EntityType), nullable=False)
    entity_id = Column(Integer, nullable=False)  # ID of the related entity
    
    # Optional specific relationships for common entities
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    
    gravity_entry_id = Column(Integer, nullable=True)  # ID of the entry in Gravity Forms
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_by_id = Column(Integer, ForeignKey('customers.id'), nullable=True)  # Usually a customer
    is_complete = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    template = relationship("FormTemplate", back_populates="submissions")
    responses = relationship("FormResponse", back_populates="submission", cascade="all, delete-orphan")
    pet = relationship("Pet", foreign_keys=[pet_id], back_populates="form_submissions")
    booking = relationship("Booking", foreign_keys=[booking_id], back_populates="form_submissions")
    customer = relationship("Customer", foreign_keys=[customer_id], back_populates="form_submissions")
    submitted_by = relationship("Customer", foreign_keys=[submitted_by_id])
    files = relationship("FormFile", back_populates="submission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FormSubmission(id={self.id}, entity_type='{self.entity_type}', entity_id={self.entity_id})>"

class FormResponse(Base):
    """Response to a single field in a form submission"""
    __tablename__ = 'form_responses'

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=False)
    field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=False)
    text_value = Column(Text, nullable=True)  # For text, textarea, email, etc.
    number_value = Column(Integer, nullable=True)  # For number fields
    json_value = Column(JSON, nullable=True)  # For multiselect, complex data
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="responses")
    field = relationship("FormField", back_populates="responses")
    
    def __repr__(self):
        return f"<FormResponse(id={self.id}, submission_id={self.submission_id}, field_id={self.field_id})>"
    
    @property
    def value(self):
        """Get the response value in the most appropriate format"""
        if self.field.field_type in [FieldType.TEXT, FieldType.TEXTAREA, FieldType.EMAIL, FieldType.PHONE, FieldType.DATE]:
            return self.text_value
        elif self.field.field_type == FieldType.NUMBER:
            return self.number_value
        elif self.field.field_type in [FieldType.SELECT, FieldType.MULTISELECT, FieldType.CHECKBOX, FieldType.RADIO]:
            return self.json_value
        else:
            return self.text_value

class FormFile(Base):
    """File uploaded as part of a form submission"""
    __tablename__ = 'form_files'

    id = Column(Integer, primary_key=True)
    submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=False)
    field_id = Column(Integer, ForeignKey('form_fields.id'), nullable=False)
    
    # For storing in cloud storage (same approach as PetDocument/MediaFile)
    original_filename = Column(String(255), nullable=True)
    object_key = Column(String(255), nullable=False)
    bucket_name = Column(String(100), nullable=False)
    content_type = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="files")
    field = relationship("FormField")
    
    def __repr__(self):
        return f"<FormFile(id={self.id}, submission_id={self.submission_id}, original_filename='{self.original_filename}')>" 