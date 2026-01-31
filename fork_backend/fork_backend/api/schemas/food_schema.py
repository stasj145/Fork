"""Pydantic schema for validation of user api."""

from typing import Optional, List
from pydantic import Field

from fork_backend.api.schemas.base_schema import ForkBaseSchema
from fork_backend.models.food_sources import Sources


class FoodIngredientBase(ForkBaseSchema):
    """Association model linking FoodItems to their sub-items with quantity"""

    quantity: float = Field(..., examples=[150.0])
    ingredient: Optional["FoodInDB"] = Field(None,
                                 description="The FoodInDB that represents the actual ingredient")


class FoodIngredientInDB(FoodIngredientBase):
    """Association model linking FoodItems to their sub-items with quantity"""

    parent_id: str = Field(..., examples=[
                           "123e4567-e89b-12d3-a456-426614174000"])
    ingredient_id: str = Field(..., examples=[
                               "123e4567-e89b-12d3-a456-426614174000"])


class FoodIngredientCreate(ForkBaseSchema):
    """Association model linking FoodItems to their sub-items with quantity"""

    parent_id: Optional[str] = Field(None, examples=[
                           "123e4567-e89b-12d3-a456-426614174000"])
    ingredient_id: str = Field(..., examples=[
                               "123e4567-e89b-12d3-a456-426614174000"])
    quantity: float = Field(..., examples=[150.0])


class FoodBase(ForkBaseSchema):
    """Shared properties"""
    name: str = Field(..., max_length=255, examples=["Apple"])
    brand: str = Field("Generic", max_length=255, examples=["Generic"])
    description: str = Field(None, max_length=1000,
                             examples=["A delicious fruit."])
    serving_size: float = Field(150.0, examples=[150.0])
    serving_unit: str = Field("serving", max_length=20, examples=["g"])
    calories_per_100: float = Field(0.0, examples=[54.0])
    protein_per_100: float = Field(0.0, examples=[0.3])
    carbs_per_100: float = Field(0.0, examples=[14.4])
    fat_per_100: float = Field(0.0, examples=[0.1])

class FoodCreate(FoodBase):
    """Properties to receive via API on creation"""
    private: bool = Field(False, examples=[False])
    hidden: Optional[bool] = Field(None, examples=[False])
    barcode: Optional[str] = Field(None, max_length=50, examples=["0123456789123"])
    ingredients: Optional[list[FoodIngredientCreate]] = Field(None, description="All, if any, ingredients of the food")


class FoodUpdate(ForkBaseSchema):
    """Properties to receive via API on update (all optional)"""
    name: Optional[str] = Field(None, max_length=255, examples=["Apple"])
    private: Optional[bool] = Field(None, examples=[False])
    hidden: Optional[bool] = Field(None, examples=[False])
    barcode: Optional[str] = Field(
        None, max_length=50, examples=["0123456789123"])
    brand: Optional[str] = Field(None, max_length=255, examples=["Generic"])
    description: Optional[str] = Field(
        None, max_length=1000, examples=["A delicious fruit."])
    serving_size: Optional[float] = Field(None, examples=[150.0])
    serving_unit: Optional[str] = Field(None, max_length=20, examples=["g"])
    calories_per_100: Optional[float] = Field(None, examples=[54.0])
    protein_per_100: Optional[float] = Field(None, examples=[0.3])
    carbs_per_100: Optional[float] = Field(None, examples=[14.4])
    fat_per_100: Optional[float] = Field(None, examples=[0.1])
    ingredients: Optional[list[FoodIngredientCreate]] = Field(None, description="All, if any, ingredients of the food")


class FoodInDB(FoodBase):
    """Properties stored in DB"""
    id: str = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    private: bool = Field(..., examples=[False])
    hidden: bool = Field(..., examples=[False])
    barcode: Optional[str] = Field(
        None, max_length=50, examples=["0123456789123"])
    img_name: Optional[str] = Field(None, max_length=40,
                                    examples=["123e4567-e89b-12d3-a456-426614174000.jpg"])

class FoodDetailed(FoodInDB):
    """
    Includes ingredients
    """
    ingredients: List[FoodIngredientInDB] = Field(
        default_factory=list, 
        description="All, if any, ingredients of the food. Max one level of recurion"
    )

class FoodSearch(ForkBaseSchema):
    """Properties for searching for food"""
    query: Optional[str] = Field(None, examples=["Nutella"])
    code: Optional[str] = Field(None, examples=["3017620422003"])
    source: Optional[Sources] = Field(
        Sources.LOCAL, examples=[Sources.LOCAL, Sources.OPENFOODFACTS])
    limit: Optional[int] = Field(20, examples=[20])


FoodIngredientBase.model_rebuild()
FoodIngredientInDB.model_rebuild()
