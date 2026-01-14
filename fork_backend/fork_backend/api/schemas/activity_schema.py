"""Pydantic schema for validation of activity api."""

from typing import Optional
from datetime import date as date_class
from pydantic import Field

from fork_backend.api.schemas.base_schema import ForkBaseSchema
from fork_backend.api.schemas.user_schema import GoalsBase
from fork_backend.models.activities import Activities


class ActivityBase(ForkBaseSchema):
    """Shared properties for Activities"""
    name: str = Field(..., description="The name of the activity")
    calories_burned_kg_h: float = Field(..., description="Calories burned per hour per kg of weight")


class ActivityCreate(ActivityBase):
    """Properties to receive via API on creation"""


class ActivityUpdate(ForkBaseSchema):
    """Properties to receive via API on update (all optional)"""
    name: Optional[str] = Field(None, description="The name of the activity")
    calories_burned_kg_h: Optional[float] = Field(None, description="Calories burned per hour per kg of weight")


class ActivityInDB(ActivityBase):
    """Properties stored in DB"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    user_id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])


class ActivityDetailed(ActivityInDB):
    """Detailed activity information"""


class ActivitySearch(ForkBaseSchema):
    """Properties for searching for activities"""
    query: Optional[str] = Field(None, examples=["Running"])
    limit: Optional[int] = Field(20, examples=[20])


class ActivityEntryBase(ForkBaseSchema):
    """Shared properties for ActivityEntry"""
    activity: ActivityInDB = Field(..., description="The specific activity performed")
    duration: float = Field(..., description="Duration of the activity in hours")
    calories_burned: Optional[float] = Field(None, description="Total calories burned")


class ActivityEntryInDB(ActivityEntryBase):
    """Properties stored in DB"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])


class ActivityLogBase(ForkBaseSchema):
    """Shared properties for ActivityLog"""
    date: date_class = Field(..., examples=["2025-01-29"])
    activity_entries: list[ActivityEntryInDB] = Field([], description="The activities performed on this day")
    goals: GoalsBase = Field(default_factory=GoalsBase, description="the users goals on this day")


class ActivityEntryUpdate(ForkBaseSchema):
    """Properties to receive via API on activity entry update"""
    duration: Optional[float] = Field(None, description="Duration of the activity in hours")
    calories_burned: Optional[float] = Field(None, description="Total calories burned")


class ActivityLogInDB(ActivityLogBase):
    """Properties stored in DB"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])


class ActivityEntryCreate(ForkBaseSchema):
    """Properties to receive via API on activity entry creation"""
    activity_id: str = Field(..., description="The ID of the activity")
    duration: float = Field(..., description="Duration of the activity in hours")
    calories_burned: Optional[float] = Field(None, description="Total calories burned")
