"""The different recognised image sizes."""

from enum import Enum

class ImageSize(str, Enum):
    """All recognised image sizes"""
    LARGE = "large"
    THUMBNAIL = "thumbnail"
