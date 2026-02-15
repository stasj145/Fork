"""Model for individual food items e.g. banana, apple, ..."""

from uuid import uuid4
from sqlalchemy import String, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from fork_backend.models.base import Base


class FoodItem(Base):
    """Singular food item"""
    __tablename__ = "food_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    private: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    hidden: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(
        String(1000), nullable=True)
    barcode: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True, unique=True)
    img_name: Mapped[str] = mapped_column(String(40), nullable=True, default=None)

    # Nutritional facts per serving
    serving_size: Mapped[float] = mapped_column(Float, nullable=False)
    serving_unit: Mapped[str] = mapped_column(
        String(20), nullable=False)
    calories_per_100: Mapped[float] = mapped_column(Float, nullable=False)
    protein_per_100: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_per_100: Mapped[float] = mapped_column(Float, nullable=False)
    fat_per_100: Mapped[float] = mapped_column(Float, nullable=False)

    # Using 384 dimensions for multilingual-e5-small
    embedding: Mapped[Vector | None] = mapped_column(
        Vector(384), nullable=True)

    # Relationships
    food_entries: Mapped[list["FoodEntry"]] = relationship(
        back_populates="food_item")
    ingredients: Mapped[list["FoodItemIngredient"]] = relationship(
        "FoodItemIngredient",
        foreign_keys="[FoodItemIngredient.parent_id]",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    # ephemeral property
    @property
    def external_image_url(self) -> str | None:
        """Url to externally hosted image. Not persisted to db"""
        return getattr(self, "_ext_image_url", None)

    @external_image_url.setter
    def external_image_url(self, value):
        self._ext_image_url = value


class FoodItemIngredient(Base):
    """Association model linking FoodItems to their sub-items with quantity"""
    __tablename__ = "food_item_ingredients"

    parent_id: Mapped[str] = mapped_column(
        ForeignKey("food_items.id", ondelete="CASCADE"), primary_key=True
    )
    ingredient_id: Mapped[str] = mapped_column(
        ForeignKey("food_items.id", ondelete="CASCADE"), primary_key=True
    )

    quantity: Mapped[float] = mapped_column(Float, nullable=False)

    parent: Mapped["FoodItem"] = relationship(
        "FoodItem", foreign_keys=[parent_id], back_populates="ingredients"
    )
    ingredient: Mapped["FoodItem"] = relationship(
        "FoodItem", foreign_keys=[ingredient_id]
    )
