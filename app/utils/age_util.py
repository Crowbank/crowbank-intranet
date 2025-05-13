"""
Age Calculation Utilities

This module provides utilities for calculating and formatting ages from dates.
"""

from datetime import date
from typing import Optional

from dateutil.relativedelta import relativedelta

def calculate_age(birth_date: date, reference_date: Optional[date] = None) -> Optional[relativedelta]:
    """
    Calculate age based on birth date.
    
    Args:
        birth_date: The date of birth
        reference_date: Date to calculate age against (defaults to today)
        
    Returns:
        A relativedelta object representing the age, or None if birth_date is None
    """
    if not birth_date:
        return None
        
    reference = reference_date or date.today()
    return relativedelta(reference, birth_date)

def format_age(age: relativedelta) -> str:
    """
    Format a relativedelta age as a human-readable string.
    
    Args:
        age: A relativedelta representing an age
        
    Returns:
        Formatted string like "3y 4m" or "2m 15d"
    """
    if not age:
        return "Unknown"
        
    if age.years > 0:
        return f"{age.years}y {age.months}m"
    elif age.months > 0:
        return f"{age.months}m {age.days}d"
    else:
        return f"{age.days}d"

def format_age_from_date(birth_date: date, reference_date: Optional[date] = None) -> str:
    """
    Calculate and format an age string directly from a birth date.
    
    Args:
        birth_date: The date of birth
        reference_date: Date to calculate age against (defaults to today)
        
    Returns:
        Formatted string like "3y 4m" or "2m 15d", or "Unknown" if birth_date is None
    """
    age = calculate_age(birth_date, reference_date)
    return format_age(age) 