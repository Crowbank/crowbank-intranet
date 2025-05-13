import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, DateTime, Date, Numeric, Table
from sqlalchemy.orm import relationship

from .base import Base
from app.models.booking import DayPeriod  # Import DayPeriod enum from booking model

# Association table for booking_intent to pets (many-to-many)
booking_intent_pets = Table(
    'booking_intent_pets',
    Base.metadata,
    Column('booking_intent_id', Integer, ForeignKey('booking_intents.id'), primary_key=True),
    Column('pet_id', Integer, ForeignKey('pets.id'), primary_key=True)
)

class BookingIntentStatus(str, enum.Enum):
    """Status of a booking intent (request)"""
    OPEN = "open"              # Initial status, waiting for staff review
    APPROVED = "approved"      # Approved and converted to a booking
    REJECTED = "rejected"      # Rejected by staff
    WAIT_LIST = "wait_list"    # Placed on wait list
    DUPLICATE = "duplicate"    # Marked as a duplicate request
    CANCELLED = "cancelled"    # Cancelled by customer

class BookingIntent(Base):
    """
    Represents a booking request, which may or may not become an actual booking.
    
    BookingIntent tracks the complete lifecycle of booking requests, from
    initial request through approval/rejection/waitlisting.
    """
    __tablename__ = 'booking_intents'

    id = Column(Integer, primary_key=True)
    
    # Request details
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)
    arrival_period = Column(Enum(DayPeriod), nullable=True)  # AM/PM preference for arrival
    departure_period = Column(Enum(DayPeriod), nullable=True)  # AM/PM preference for departure
    
    # Customer input details
    comments = Column(Text, nullable=True)
    destination = Column(String(255), nullable=True)  # Where the pet owner is going
    
    # Status and workflow tracking
    status = Column(Enum(BookingIntentStatus), nullable=False, default=BookingIntentStatus.OPEN)
    status_notes = Column(Text, nullable=True)  # Notes about status changes
    auto_approved = Column(Boolean, default=False, nullable=False)  # Whether this was auto-approved
    
    # Form connection (if created from form)
    gravity_form_id = Column(Integer, nullable=True)
    gravity_entry_id = Column(Integer, nullable=True)
    form_submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)  # When approved/rejected/waitlisted
    
    # If marked as duplicate, reference to the primary intent
    duplicate_of_id = Column(Integer, ForeignKey('booking_intents.id'), nullable=True)
    
    # Foreign Keys
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Employee who handled this request
    handled_by_id = Column(Integer, ForeignKey('employees.id'), nullable=True)
    
    # Relationships
    pets = relationship("Pet", secondary=booking_intent_pets, back_populates="booking_intents")
    customer = relationship("Customer", back_populates="booking_intents")
    form_submission = relationship("FormSubmission")
    handled_by = relationship("Employee")
    
    # Connection to resulting booking (if approved)
    booking = relationship("Booking", back_populates="booking_intent", uselist=False)
    
    # Other duplicate requests of this intent
    duplicates = relationship("BookingIntent", 
                             foreign_keys=[duplicate_of_id],
                             backref="duplicate_of")
    
    def __repr__(self):
        pet_count = len(self.pets) if self.pets else 0
        return f"<BookingIntent(id={self.id}, pets={pet_count}, arrival={self.arrival_date}, status='{self.status}')>"
    
    @property
    def is_active(self):
        """Whether this booking intent is still active (not approved, rejected, or duplicate)"""
        return self.status in [BookingIntentStatus.OPEN, BookingIntentStatus.WAIT_LIST]
    
    @property
    def is_daycare(self):
        """
        Check if this is a daycare booking intent (same day arrival and departure).
        
        Returns:
            Boolean indicating if this is a daycare booking intent
        """
        return self.arrival_date == self.departure_date
    
    @property
    def duration_days(self):
        """Calculate the duration of the intended stay in days"""
        if not self.arrival_date or not self.departure_date:
            return 0
        return (self.departure_date - self.arrival_date).days
    
    def approve(self, employee_id=None, auto=False):
        """
        Approve this booking intent and update its status.
        
        Args:
            employee_id: ID of the employee who approved it (None if auto-approved)
            auto: Whether this was auto-approved
            
        Returns:
            True if the status was changed, False if already approved
        """
        if self.status == BookingIntentStatus.APPROVED:
            return False
            
        self.status = BookingIntentStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.handled_by_id = employee_id
        self.auto_approved = auto
        return True
        
    def reject(self, employee_id, notes=None):
        """
        Reject this booking intent.
        
        Args:
            employee_id: ID of the employee who rejected it
            notes: Optional notes explaining rejection
            
        Returns:
            True if the status was changed, False if already rejected
        """
        if self.status == BookingIntentStatus.REJECTED:
            return False
            
        self.status = BookingIntentStatus.REJECTED
        self.approved_at = datetime.utcnow()  # Using same field for rejection timestamp
        self.handled_by_id = employee_id
        if notes:
            self.status_notes = notes
        return True
        
    def waitlist(self, employee_id, notes=None):
        """
        Add this booking intent to the waitlist.
        
        Args:
            employee_id: ID of the employee who waitlisted it
            notes: Optional notes explaining waitlist decision
            
        Returns:
            True if the status was changed, False if already on waitlist
        """
        if self.status == BookingIntentStatus.WAIT_LIST:
            return False
            
        self.status = BookingIntentStatus.WAIT_LIST
        self.approved_at = datetime.utcnow()  # Using same field for waitlist timestamp
        self.handled_by_id = employee_id
        if notes:
            self.status_notes = notes
        return True
        
    def mark_as_duplicate(self, primary_intent_id, employee_id, notes=None):
        """
        Mark this booking intent as a duplicate of another.
        
        Args:
            primary_intent_id: ID of the primary booking intent
            employee_id: ID of the employee who marked it as duplicate
            notes: Optional notes
            
        Returns:
            True if the status was changed, False if already marked as duplicate
        """
        if self.status == BookingIntentStatus.DUPLICATE:
            return False
            
        self.status = BookingIntentStatus.DUPLICATE
        self.duplicate_of_id = primary_intent_id
        self.handled_by_id = employee_id
        if notes:
            self.status_notes = notes
        return True 