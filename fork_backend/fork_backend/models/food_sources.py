"""The different recognised sources to search for food in."""

from enum import Enum

class Sources(str, Enum):
    """All recognised gender types for BMR calc"""
    LOCAL = "local"
    PERSONAL = "personal"
    OPENFOODFACTS = "openfoodfacts"
