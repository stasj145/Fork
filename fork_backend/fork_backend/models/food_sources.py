"""The different recognised sources to search for food in."""

from enum import Enum

class Sources(str, Enum):
    """All recognised sources for food search"""
    LOCAL = "local"
    PERSONAL = "personal"
    OPENFOODFACTS = "openfoodfacts"
    TANDOOR = "tandoor"
