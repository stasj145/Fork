"""The different recognised gender types for BMR calc."""

from enum import Enum

class Gender(str, Enum):
    """All recognised gender types for BMR calc"""
    MALE = "male"
    FEMALE = "female"
