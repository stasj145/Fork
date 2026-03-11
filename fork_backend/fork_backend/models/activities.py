"""Data model for base activities"""
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base


class Activities(Base):
    """The log of all activities that are known"""
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    private: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)

    # amount of calories that are burned per hour and kg of weight
    calories_burned_kg_h: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    activity_entries: Mapped[list["ActivityEntry"]
                             ] = relationship(back_populates="activity")
