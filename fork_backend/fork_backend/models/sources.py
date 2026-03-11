"""The different recognised sources to search for food in."""

from enum import Enum


class FoodSources(str, Enum):
    """All recognised sources for food search"""
    LOCAL = "local"
    PERSONAL = "personal"
    OPENFOODFACTS = "openfoodfacts"
    TANDOOR = "tandoor"


class ActivitySources(str, Enum):
    """All recognised sources for activity search"""
    LOCAL = "local"
    PERSONAL = "personal"
