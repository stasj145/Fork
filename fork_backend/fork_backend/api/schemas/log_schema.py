"""Pydantic schema for validation of user api."""

from typing import Optional
from datetime import date as date_class
from pydantic import Field

from fork_backend.api.schemas.base_schema import ForkBaseSchema
from fork_backend.api.schemas.user_schema import GoalsBase
from fork_backend.api.schemas.food_schema import FoodDetailed
from fork_backend.models.meal_type import MealType


class FoodEntryBase(ForkBaseSchema):
    """Shared properties FoodEntry"""
    food_item: FoodDetailed = Field(..., description="The specific food item the user has eaten")
    meal_type: MealType = Field(..., description="What type of meal this was.")
    quantity: float = Field(..., description="How much of the food was eaten in g.",
                            examples=["100"])

class FoodEntryInDB(FoodEntryBase):
    """Properties stored in DB"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])

class LogBase(ForkBaseSchema):
    """Shared properties for FoodLog"""
    date: date_class = Field(..., examples=["2025-01-29"])
    notes: Optional[str] = Field("", max_length=10000, examples=["Some notes for this log"])
    food_entries: list[FoodEntryInDB] = Field([], description="The food the user has eaten on this day")
    goals: GoalsBase = Field(default_factory=GoalsBase, description="the users goals on this day")

class FoodUpdate(ForkBaseSchema):
    """Properties to receive via API on update (all optional)"""
    notes: Optional[str] = Field("", max_length=10000, examples=["Some notes for this log"])

class FoodEntryUpdate(ForkBaseSchema):
    """Properties to receive via API on food entry update"""
    meal_type: Optional[MealType] = Field(None, description="What type of meal this was.")
    quantity: Optional[float] = Field(None, description="How much of the food was eaten in g.",
                                      examples=["100"])

class LogInDB(LogBase):
    """Properties stored in DB"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])

class FoodEntryCreate(ForkBaseSchema):
    """Properties to receive via API on food entry creation"""
    food_id: str = Field(..., description="The ID of the food item")
    quantity: float = Field(..., description="How much of the food was eaten in g.",
                            examples=["100"])
    meal_type: MealType = Field(..., description="What type of meal this was.")
