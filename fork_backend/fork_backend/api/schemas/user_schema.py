"""Pydantic schema for validation of user api."""

from typing import Optional
from pydantic import EmailStr, Field

from fork_backend.api.schemas.base_schema import ForkBaseSchema
from fork_backend.models.gender import Gender
from fork_backend.models.activity_levels import ActivityLevels

class GoalsBase(ForkBaseSchema):
    """Goal properties"""
    daily_calorie_target: int = Field(2000, ge=0, examples=[2000])
    daily_protein_target: int = Field(65, ge=0, examples=[65])
    daily_carbs_target: int = Field(250, ge=0, examples=[250])
    daily_fat_target: int = Field(60, ge=0, examples=[60])
    daily_calorie_burn_target: int = Field(200, ge=0, examples=[200])


class UserBase(ForkBaseSchema):
    """Shared properties"""
    username: str = Field(..., max_length=255, examples=["johndoe"])
    email: EmailStr = Field(..., max_length=255, examples=["john@example.com"])
    goals: GoalsBase = Field(GoalsBase(), description="the users goals")
    weight: float = Field(85.4, ge=0, examples=[85.4])
    height: float = Field(180.0, ge=0, examples=[180.0])
    age: int = Field(18, ge=0, examples=[18])
    gender: Gender = Field(Gender.MALE, examples=[Gender.MALE, Gender.FEMALE])
    activity_level: ActivityLevels = Field(ActivityLevels.SEDENTARY, examples=[
        ActivityLevels.SEDENTARY])


class UserCreate(UserBase):
    """Properties to receive via API on creation"""
    password: str = Field(..., min_length=8, max_length=255, examples=["secretpassword"])

class UserUpdate(ForkBaseSchema):
    """Properties to receive via API on update (all optional)"""
    username: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=255)
    goals: Optional[GoalsBase] = Field(None, description="the users goals")
    weight: Optional[float] = Field(None, ge=0, examples=[85.4])
    height: Optional[float] = Field(None, ge=0, examples=[180.0])
    age: Optional[int] = Field(None, ge=0, examples=[18])
    gender: Optional[Gender] = Field(None, examples=[Gender.MALE, Gender.FEMALE])
    activity_level: Optional[ActivityLevels] = Field(None, examples=[
        ActivityLevels.SEDENTARY])


class UserInDB(UserBase):
    """Properties stored in DB (excluding pw hash)"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
