"""The different recognised activity levels."""

from enum import Enum

class ActivityLevels(str, Enum):
    """All recognised activity levels"""
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE  = "moderately_active"
    VERY_ACTIVE  = "very_active"
    SUPER_ACTIVE   = "super_active"
