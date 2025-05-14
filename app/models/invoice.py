import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, DateTime, Date, Numeric, func
from sqlalchemy.orm import relationship, column_property

from .base import Base

class PaymentType(str, enum.Enum):
    """Types of payment methods"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    STRIPE = "stripe"
    OTHER = "other"
    CREDIT = "credit"
    VOUCHER = "voucher"

class ChargeType(str, enum.Enum):
    """Types of charges on an invoice"""
    BOOKING = "booking"         # Services related to the initial booking
    TRANSPORT = "transport"     # Services related to transport
    BOARDING = "boarding"       # Per-day boarding charges
    ADHOC = "adhoc"             # Ad-hoc services added during the stay
    ADJUSTMENT = "adjustment"   # Manual adjustments to the invoice
    VET_BILL = "vet_bill"       # Vet bills

class Invoice(Base):
    """
    Represents an invoice for a booking, containing charges and payments.
    """
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False, unique=True)
    
    # Discount structure
    percentage_discount = Column(Numeric(5, 2), nullable=False, default=0)  # As percentage (0-100)
    absolute_discount = Column(Numeric(10, 2), nullable=False, default=0)   # Fixed amount
    
    # Invoice status
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="invoice")
    charges = relationship("Charge", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    # Calculated properties
    gross_amount = column_property(
        func.coalesce(
            func.sum(func.coalesce("Charge.amount", 0)),
            0
        ).label("gross_amount")
    )
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, booking_id={self.booking_id}, gross={self.gross_amount})>"
    
    @property
    def total_discount(self):
        """
        Calculate the total discount amount.
        
        Returns:
            The greater of percentage discount or absolute discount
        """
        if not self.gross_amount:
            return 0
            
        percentage_amount = (self.percentage_discount / 100) * self.gross_amount
        return max(percentage_amount, self.absolute_discount)
    
    @property
    def net_amount(self):
        """
        Calculate the net amount after discount.
        
        Returns:
            Gross amount less total discount
        """
        return self.gross_amount - self.total_discount
    
    @property
    def amount_paid(self):
        """
        Calculate the total amount paid.
        
        Returns:
            Sum of all payment amounts
        """
        return sum(payment.amount for payment in self.payments)
    
    @property
    def amount_outstanding(self):
        """
        Calculate the outstanding amount.
        
        Returns:
            Net amount less amount paid
        """
        return self.net_amount - self.amount_paid
    
    @property
    def is_paid(self):
        """
        Check if the invoice is fully paid.
        
        Returns:
            True if amount_outstanding <= 0, False otherwise
        """
        return self.amount_outstanding <= 0

class Charge(Base):
    """
    Represents a single charge on an invoice.
    """
    __tablename__ = 'charges'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    
    # Optional associations
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=True)
    date = Column(Date, nullable=True)  # For date-specific charges like boarding
    
    # Charge details
    charge_type = Column(Enum(ChargeType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Numeric(5, 2), nullable=False, default=1)  # For multiple days or units
    is_quantity_overridden = Column(Boolean, default=False, nullable=False)  # Whether quantity was manually set
    is_rate_overridden = Column(Boolean, default=False, nullable=False)  # Whether rate was manually set
    is_peak = Column(Boolean, default=False, nullable=False)  # Whether this is a peak date charge (for premium pricing)
    minimum_days = Column(Integer, nullable=True)  # Booking-specific minimum days override
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="charges")
    service = relationship("Service", back_populates="charges")
    pet = relationship("Pet", backref="charges")
    
    def __repr__(self):
        pet_info = f", pet_id={self.pet_id}" if self.pet_id else ""
        date_info = f", date={self.date}" if self.date else ""
        peak_info = ", peak=True" if self.is_peak else ""
        return f"<Charge(id={self.id}, service='{self.service.code if self.service else None}', amount={self.amount}{pet_info}{date_info}{peak_info})>"

class Payment(Base):
    """
    Represents a payment made against an invoice.
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    
    # Payment details
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    payment_date = Column(Date, default=datetime.utcnow().date, nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    
    # Financial details
    amount = Column(Numeric(10, 2), nullable=False)
    fees = Column(Numeric(10, 2), nullable=False, default=0)  # Processing fees
    reference = Column(String(100), nullable=True)  # For tracking payment references
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", backref="payments")
    
    @property
    def net_amount(self):
        """
        Calculate the net amount after fees.
        
        Returns:
            Amount less fees
        """
        return self.amount - self.fees
    
    def __repr__(self):
        return f"<Payment(id={self.id}, type='{self.payment_type}', amount={self.amount}, date={self.payment_date})>" 