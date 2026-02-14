"""
Schema for image api endpoints.
"""

from pydantic import Field, HttpUrl

from fork_backend.api.schemas.base_schema import ForkBaseSchema

class RequestImage(ForkBaseSchema):
    """Schema for requesting an image"""
    name: str = Field(..., max_length=40, examples=["123e4567-e89b-12d3-a456-426614174000.jpg"])

class ImageUrl(ForkBaseSchema):
    """Schema for image URL"""
    url: HttpUrl = Field(..., description="URL of the image to download and process")
