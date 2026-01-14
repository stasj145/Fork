"""Data model to log all days where food is consumed"""
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base


class FoodLog(Base):
    """The log of all date where food is consumed"""
    __tablename__ = "food_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(Date, nullable=False, index=True)
    goals_id: Mapped[str] = mapped_column(String(36), ForeignKey("goals.id"), nullable=False)
    notes: Mapped[str] = mapped_column(String(1000), default="")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="food_log")
    food_entries: Mapped[list["FoodEntry"]] = relationship(
        back_populates="food_log", cascade="all, delete-orphan")

    goals: Mapped["Goals"] = relationship(foreign_keys=[goals_id])