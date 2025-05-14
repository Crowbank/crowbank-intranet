from typing import Optional
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base
from .mixins import AddressMixin

class Vet(Base, AddressMixin):
    __tablename__ = 'vets'

    id = Column(Integer, primary_key=True)
    practice_name: Mapped[str] = mapped_column(String(100))
    street = Column(String(255), nullable=True)
    town = Column(String(100), nullable=True)
    postcode = Column(String(20), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    website: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationship back to Customers who have this vet as default (optional)
    customers = relationship("Customer", back_populates="default_vet")
    
    # Relationship to pets that use this vet
    pets = relationship("Pet", back_populates="default_vet")

    def __repr__(self):
        return f"<Vet(id={self.id}, practice_name='{self.practice_name}')>" 