"""
Model mixins for Crowbank Intranet.

This module contains SQLAlchemy model mixins that can be reused across models.
"""

from typing import Optional
from sqlalchemy import Column, String


class AddressMixin:
    """
    Mixin for models that contain address information.
    
    This can be used by Customer, Vet, and other models that need address fields.
    """
    
    street = Column(String(100), nullable=True)
    town = Column(String(50), nullable=True)
    county = Column(String(50), nullable=True)
    postcode = Column(String(10), nullable=True)
    
    def get_full_address(self) -> str:
        """
        Get the full address as a formatted string.
        
        Returns:
            Formatted address string
        """
        parts = []
        if self.street:
            parts.append(self.street)
        if self.town:
            parts.append(self.town)
        if self.county:
            parts.append(self.county)
        if self.postcode:
            parts.append(self.postcode)
        
        return ", ".join(parts)
    
    def get_navigation_url(self) -> Optional[str]:
        """
        Get a URL for navigation to this address.
        
        Returns:
            Google Maps URL for the address or None if no postcode
        """
        if not self.postcode:
            return None
        
        # Create a Google Maps URL with the postcode
        # Optionally include additional address components
        address_parts = []
        if self.street:
            address_parts.append(self.street.replace(" ", "+"))
        if self.town:
            address_parts.append(self.town.replace(" ", "+"))
        if self.county:
            address_parts.append(self.county.replace(" ", "+"))
        address_parts.append(self.postcode.replace(" ", "+"))
        
        address_str = ",".join(address_parts)
        return f"https://www.google.com/maps/search/?api=1&query={address_str}"


class ContactDetailsMixin:
    """
    Mixin for models that contain contact information.
    
    This can be used by Customer, Vet, Contact, and other models that need contact fields.
    """
    
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    def get_primary_contact(self) -> Optional[str]:
        """
        Get the primary contact method.
        
        Returns:
            The first available contact method in order: mobile, phone, email
        """
        if self.mobile:
            return self.mobile
        if self.phone:
            return self.phone
        if self.email:
            return self.email
        return None
