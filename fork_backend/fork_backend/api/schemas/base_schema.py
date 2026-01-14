"""Pydantic schema for validation of user api."""

from pydantic import BaseModel, ConfigDict

class ForkBaseSchema(BaseModel):
    """base pydantic schema"""
    model_config = ConfigDict(from_attributes=True)
