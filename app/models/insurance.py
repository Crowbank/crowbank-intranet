from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import date

from .base import Base

class Insurance(Base):
    __tablename__ = 'insurance'

    id = Column(Integer, primary_key=True)
    policy_number = Column(String(50), nullable=True)
    provider = Column(String(100), nullable=False)
    coverage_level = Column(String(100), nullable=True)  # E.g., "Basic", "Premium", "Comprehensive"
    start_date = Column(Date, nullable=True)
    renewal_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    pets = relationship("Pet", back_populates="insurance")
    
    def __repr__(self):
        return f"<Insurance(id={self.id}, provider='{self.provider}', policy='{self.policy_number}')>"
    
    @property
    def is_expired(self):
        """Check if the insurance policy is expired."""
        if not self.renewal_date:
            return False
        return self.renewal_date < date.today() 