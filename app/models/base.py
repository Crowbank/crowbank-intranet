"""
Base model class and mixins for Crowbank Intranet.

All models should inherit from the Base class defined here.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative models
Base = declarative_base()


class CrowbankBase:
    """
    Base mixin class for all Crowbank models.
    
    Provides common fields and methods for all models.
    """
    
    # Primary key column using auto-increment
    id = Column(Integer, primary_key=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary representation.
        
        Useful for APIs and serialization.
        
        Returns:
            Dictionary representation of the model.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def get_by_id(cls, session, model_id: int) -> Optional[Any]:
        """
        Get model instance by ID.
        
        Args:
            session: SQLAlchemy session
            model_id: ID of the model to retrieve
            
        Returns:
            Model instance if found, otherwise None
        """
        return session.query(cls).filter(cls.id == model_id).first()
