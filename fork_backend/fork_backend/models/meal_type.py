"""The different recognised meal types."""

from enum import Enum

class MealType(str, Enum):
    """All recognised meal types"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
