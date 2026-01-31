"""
Schema for image api endpoints.
"""

from pydantic import Field

from fork_backend.api.schemas.base_schema import ForkBaseSchema

class RequestImage(ForkBaseSchema):
    """Schema for requesting an image"""
    name: str = Field(..., max_length=40, examples=["123e4567-e89b-12d3-a456-426614174000.jpg"])
