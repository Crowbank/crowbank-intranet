"""
Models package for Crowbank Intranet.

This package contains SQLAlchemy model definitions for the application.
"""

from app.models.base import Base

# Import models to make them available when importing the package
# from app.models.customer import Customer, Contact, CustomerContact
# from app.models.pet import Pet
# from app.models.vet import Vet
# from app.models.booking import Booking

# Export models
__all__ = [
    'Base',
    # 'Customer', 'Contact', 'CustomerContact',
    # 'Pet',
    # 'Vet',
    # 'Booking',
] 