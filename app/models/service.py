import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, Numeric, Date
from sqlalchemy.orm import relationship

from .base import Base

class RateType(str, enum.Enum):
    """Types of service rate structures"""
    BY_SPECIES = "by_species"       # Different rates for dogs vs cats
    BY_BREED_TYPE = "by_breed_type" # Different rates by breed size/type
    BY_RANGE = "by_range"           # Different rates by distance/range
    FIXED = "fixed"                 # Same rate for all

class ServiceType(str, enum.Enum):
    """Categories of services"""
    BOARDING = "boarding"           # Core boarding service
    TRANSPORT = "transport"         # Pickup/dropoff service
    GROOMING = "grooming"           # Bathing, grooming
    DAYCARE = "daycare"             # Daycare service
    ADMIN = "admin"                 # Booking fees, administrative charges
    OTHER = "other"                 # Miscellaneous services

class ServiceApplicability(str, enum.Enum):
    """When/how services are applied"""
    PER_BOOKING = "per_booking"     # Once per booking (e.g., booking fee)
    PER_PET = "per_pet"             # Once per pet (e.g., one-time fee)
    PER_PET_DAY = "per_pet_day"     # Per pet, per day (e.g., boarding)
    PER_TRANSPORT = "per_transport" # Applied at check-in/out for transport
    ADHOC = "adhoc"                 # Applied manually as needed

class RangeCategory(str, enum.Enum):
    """Distance ranges for transport services"""
    LOCAL = "local"                 # Short distance
    MEDIUM = "medium"               # Medium distance
    EXTENDED = "extended"           # Longer distance

class Season(str, enum.Enum):
    """Seasons for seasonal pricing and policies"""
    STANDARD = "standard"           # Regular season
    PEAK = "peak"                   # Peak/high season
    LOW = "low"                     # Low/off season
    HOLIDAY = "holiday"             # Holiday periods

class LegacyRange(enum.IntEnum):
    LOCAL = 1
    MEDIUM = 2
    FAR = 3

class Service(Base):
    """
    Represents a service that can be provided and charged to customers.
    """
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Service classification
    service_type = Column(Enum(ServiceType), nullable=False)
    applicability = Column(Enum(ServiceApplicability), nullable=False)
    
    # Rate structure
    rate_type = Column(Enum(RateType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Peak pricing multiplier
    peak_rate_multiplier = Column(Numeric(5, 2), nullable=False, default=2.0)  # Default to double rate for peak dates
    
    # Minimum days for boarding services
    min_days_standard = Column(Integer, nullable=True)  # Minimum days in standard season
    min_days_peak = Column(Integer, nullable=True)      # Minimum days in peak season
    min_days_low = Column(Integer, nullable=True)       # Minimum days in low season
    min_days_holiday = Column(Integer, nullable=True)   # Minimum days in holiday periods
    
    # Relationships
    rates = relationship("ServiceRate", back_populates="service", cascade="all, delete-orphan")
    charges = relationship("Charge", back_populates="service")
    
    def __repr__(self):
        return f"<Service(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    def get_min_days(self, season=Season.STANDARD):
        """
        Get the minimum days charge for this service based on the season.
        
        Args:
            season: Season enum value
            
        Returns:
            Minimum days or None if not applicable
        """
        if self.service_type != ServiceType.BOARDING and self.applicability != ServiceApplicability.PER_PET_DAY:
            return None
            
        if season == Season.PEAK:
            return self.min_days_peak
        elif season == Season.LOW:
            return self.min_days_low
        elif season == Season.HOLIDAY:
            return self.min_days_holiday
        else:  # STANDARD
            return self.min_days_standard
    
    def get_rate(self, category=None, species=None, breed_type=None, is_peak=False):
        """
        Get the appropriate rate for this service based on its rate type.
        
        Args:
            category: For BY_RANGE services, the RangeCategory
            species: For BY_SPECIES services, the species ID
            breed_type: For BY_BREED_TYPE services, the breed type/size
            is_peak: Whether to apply peak date pricing
            
        Returns:
            The rate amount, or None if no matching rate found
        """
        base_rate = None
        
        if self.rate_type == RateType.FIXED:
            # For fixed rates, there should be only one rate with no category
            for rate in self.rates:
                if rate.category is None:
                    base_rate = rate.rate
                    break
                    
        elif self.rate_type == RateType.BY_SPECIES and species:
            # Find rate matching the species
            for rate in self.rates:
                if rate.category == str(species):
                    base_rate = rate.rate
                    break
                    
        elif self.rate_type == RateType.BY_BREED_TYPE and breed_type:
            # Find rate matching the breed type
            for rate in self.rates:
                if rate.category == breed_type:
                    base_rate = rate.rate
                    break
                    
        elif self.rate_type == RateType.BY_RANGE and category:
            # Find rate matching the range category
            for rate in self.rates:
                if rate.category == category:
                    base_rate = rate.rate
                    break
        
        # Apply peak multiplier if applicable
        if base_rate is not None and is_peak:
            return base_rate * self.peak_rate_multiplier
            
        return base_rate

class ServiceRate(Base):
    """
    Stores the rate for a specific service, which can vary based on
    species, breed type, or distance range. The 'category_legacy' column
    is an integer corresponding to the legacy identifier for species,
    breed type, or range (see LegacyRange enum for range-based rates).
    The 'category' column is the mapped new database ID or enum value.
    """
    __tablename__ = 'service_rates'

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    
    # Legacy category: species, breed type, or range enum (as integer)
    category_legacy = Column(Integer, nullable=True)
    # New category: mapped to new DB id or enum (as integer)
    category = Column(Integer, nullable=True)
    rate = Column(Numeric(10, 2), nullable=False)
    season = Column(Enum(Season), default=Season.STANDARD, nullable=False)  # For seasonal pricing
    
    # Date range for temporary rate changes (e.g., special promotions)
    effective_from = Column(Date, nullable=True)
    effective_to = Column(Date, nullable=True)
    
    # Relationship
    service = relationship("Service", back_populates="rates")
    
    def __repr__(self):
        season_info = f", season={self.season}" if self.season != Season.STANDARD else ""
        return f"<ServiceRate(service_id={self.service_id}, category_legacy={self.category_legacy}, category={self.category}, rate={self.rate}{season_info})>"

class PeakDate(Base):
    """
    Defines specific calendar dates with peak pricing (like Christmas, New Year's).
    These dates help determine which charges should be marked as peak.
    """
    __tablename__ = 'peak_dates'
    
    id = Column(Integer, primary_key=True)
    
    # Date definition
    date = Column(Date, nullable=False, unique=True)  # The specific calendar date
    name = Column(String(100), nullable=False)  # Name of holiday/special day
    is_active = Column(Boolean, default=True, nullable=False)  # For temporarily disabling
    
    def __repr__(self):
        return f"<PeakDate(date={self.date}, name='{self.name}')>" 