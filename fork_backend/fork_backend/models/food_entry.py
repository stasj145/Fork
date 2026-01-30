"""Model for all eaten food"""
from uuid import uuid4
from sqlalchemy import String, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base
from fork_backend.models.meal_type import MealType


class FoodEntry(Base):
    """Model for all eaten food"""

    __tablename__ = "food_entries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("food_logs.id"), nullable=False, index=True)
    food_id: Mapped[str] = mapped_column(
        ForeignKey("food_items.id"), nullable=False, index=True)

    quantity: Mapped[float] = mapped_column(
        Float, nullable=False) 
    meal_type: Mapped[MealType] = mapped_column(
        SQLEnum(MealType), nullable=False, default=MealType.SNACK)

    # Relationships
    food_log: Mapped["FoodLog"] = relationship(back_populates="food_entries")
    food_item: Mapped["FoodItem"] = relationship(back_populates="food_entries")
