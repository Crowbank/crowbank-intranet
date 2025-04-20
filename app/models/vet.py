from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base

class Vet(Base):
    __tablename__ = 'vets'

    id = Column(Integer, primary_key=True)
    practice_name = Column(String(200), nullable=False)
    street = Column(String(255), nullable=True)
    town = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    phone = Column(String(30), nullable=True) # Renamed from phone_number for consistency
    email = Column(String(255), nullable=True) # Renamed from email_address
    website = Column(Text, nullable=True)

    # Relationship back to Customers who have this vet as default (optional)
    # default_customers = relationship("Customer", back_populates="default_vet")

    def __repr__(self):
        return f"<Vet(id={self.id}, practice_name='{self.practice_name}')>" 