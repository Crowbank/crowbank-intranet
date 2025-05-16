import enum
from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, DateTime, Date, Numeric, Table, Time
from sqlalchemy.orm import relationship

from .base import Base

# Association table for booking to pets (many-to-many)
# booking_pets = Table(
#     'booking_pets',
#     Base.metadata,
#     Column('booking_id', Integer, ForeignKey('bookings.id'), primary_key=True),
#     Column('pet_id', Integer, ForeignKey('pets.id'), primary_key=True)
# )

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class BoardingType(str, enum.Enum):
    STANDARD = "standard"
    DELUXE = "deluxe"
    CATTERY = "cattery"
    DAYCARE = "daycare"

class DayPeriod(str, enum.Enum):
    AM = "am"
    PM = "pm"

class BookingPet(Base):
    """
    Association model for Booking-Pet relationship.
    
    Stores pet-specific details for each booking, such as medication
    and feeding instructions that may differ for each pet.
    """
    __tablename__ = 'booking_pets'
    
    # Primary keys also serve as foreign keys to the associated tables
    booking_id = Column(Integer, ForeignKey('bookings.id'), primary_key=True)
    pet_id = Column(Integer, ForeignKey('pets.id'), primary_key=True)
    
    # Pet-specific instructions for this booking
    requires_medication = Column(Boolean, default=False, nullable=False)
    medication_instructions = Column(Text, nullable=True)
    feeding_instructions = Column(Text, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="pet_bookings")
    pet = relationship("Pet", back_populates="booking_details")
    
    def __repr__(self):
        return f"<BookingPet(booking_id={self.booking_id}, pet_id={self.pet_id})>"

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    legacy_bk_no = Column(Integer, nullable=True, unique=True)
    
    # Booking dates and times
    arrival_date = Column(Date, nullable=False)
    departure_date = Column(Date, nullable=False)
    arrival_time = Column(Time, nullable=True)
    departure_time = Column(Time, nullable=True)
    
    # Status
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    
    # Additional info
    boarding_type = Column(Enum(BoardingType), nullable=False, default=BoardingType.STANDARD)
    special_instructions = Column(Text, nullable=True)
    destination = Column(String(255), nullable=True)  # Where the pet owner is going
    
    # Check-in/out timestamps
    checked_in_at = Column(DateTime, nullable=True)
    checked_out_at = Column(DateTime, nullable=True)
    
    # Pricing
    discount_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    total_cost = Column(Numeric(10, 2), nullable=True)  # Calculated when confirmed
    deposit_paid = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Foreign Keys
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    assigned_run_id = Column(Integer, ForeignKey('boarding_runs.id'), nullable=True)
    
    # Relationships
    pet_bookings = relationship("BookingPet", back_populates="booking")
    pets = relationship("Pet", secondary="booking_pets", viewonly=True)
    customer = relationship("Customer", back_populates="bookings")
    assigned_run = relationship("BoardingRun", back_populates="bookings")
    daily_allocations = relationship("DailyAllocation", back_populates="booking")
    form_submissions = relationship("FormSubmission", foreign_keys="FormSubmission.booking_id", back_populates="booking")
    
    # Connection to booking intent (if created from an intent)
    booking_intent = relationship("BookingIntent", back_populates="booking")
    
    # Invoice relationship (one-to-one)
    invoice = relationship("Invoice", back_populates="booking", uselist=False)
    
    def __repr__(self):
        pet_count = len(self.pets) if self.pets else 0
        return f"<Booking(id={self.id}, pets={pet_count}, arrival={self.arrival_date}, departure={self.departure_date}, status='{self.status}', legacy_bk_no={self.legacy_bk_no})>"
    
    @property
    def is_daycare(self):
        """
        Check if this is a daycare booking (same day arrival and departure).
        
        Returns:
            Boolean indicating if this is a daycare booking
        """
        return self.arrival_date == self.departure_date
    
    @property
    def arrival_period(self):
        """
        Determine if the arrival time is AM or PM using 1PM as the cutoff.
        
        Returns:
            DayPeriod enum indicating AM or PM
        """
        if not self.arrival_time:
            return None
        
        cutoff = time(13, 0)  # 1:00 PM
        return DayPeriod.AM if self.arrival_time < cutoff else DayPeriod.PM
    
    @property
    def departure_period(self):
        """
        Determine if the departure time is AM or PM using 1PM as the cutoff.
        
        Returns:
            DayPeriod enum indicating AM or PM
        """
        if not self.departure_time:
            return None
        
        cutoff = time(13, 0)  # 1:00 PM
        return DayPeriod.AM if self.departure_time < cutoff else DayPeriod.PM
    
    @property
    def duration_days(self):
        """Calculate the duration of the stay in days"""
        if not self.arrival_date or not self.departure_date:
            return 0
        return (self.departure_date - self.arrival_date).days + (1 if not self.is_daycare else 0)
    
    def get_form_submissions(self, form_type=None):
        """
        Get form submissions for this booking, optionally filtered by form type.
        
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
        Check if this booking has a completed form of the specified type.
        
        Args:
            form_type: FormType enum value to check for
            
        Returns:
            Boolean indicating if a completed form exists
        """
        return any(s.is_complete and s.template.type == form_type for s in self.form_submissions)
    
    def has_checkin_form(self):
        """
        Check if this booking has a completed check-in form.
        
        Returns:
            Boolean indicating if a completed check-in form exists
        """
        from app.models.form import FormType
        return self.has_completed_form(FormType.CHECKIN_FORM)
        
    def get_pet_details(self, pet_id):
        """
        Get specific details for a pet in this booking.
        
        Args:
            pet_id: ID of the pet to get details for
            
        Returns:
            BookingPet instance or None if pet not in this booking
        """
        for pet_booking in self.pet_bookings:
            if pet_booking.pet_id == pet_id:
                return pet_booking
        return None 