from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from urllib.parse import quote

class AddressMixin:
    """Mixin for models that have address fields."""
    
    street: Mapped[Optional[str]] = mapped_column(String(255))
    town: Mapped[Optional[str]] = mapped_column(String(100))
    postcode: Mapped[Optional[str]] = mapped_column(String(20))

    @property
    def has_full_address(self) -> bool:
        """Check if all address fields are populated."""
        return all([self.street, self.town, self.postcode])
    
    @property
    def full_address(self) -> Optional[str]:
        """Get formatted full address string."""
        if not self.has_full_address:
            return None
        return f"{self.street}, {self.town} {self.postcode}"
    
    def get_maps_url(self, maps_type: str = "search") -> Optional[str]:
        """Generate Google Maps URL for the address.
        
        Args:
            maps_type: Either 'search' or 'directions'
        """
        if not self.has_full_address:
            return None
            
        base_url = "https://www.google.com/maps"
        encoded_address = quote(f"{self.street}, {self.town}, {self.postcode}, UK")
        
        if maps_type == "directions":
            return f"{base_url}/dir/?api=1&destination={encoded_address}"
        return f"{base_url}/search/?api=1&query={encoded_address}" 