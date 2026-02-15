"""goal model"""

from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base

class Goals(Base):
    """User model"""
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                 nullable=False)
    daily_calorie_target: Mapped[int] = mapped_column(Integer, nullable=False, default=2000)
    daily_protein_target: Mapped[int] = mapped_column(Integer, nullable=False, default=65)
    daily_carbs_target: Mapped[int] = mapped_column(Integer, nullable=False, default=250)
    daily_fat_target: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    daily_calorie_burn_target: Mapped[int] = mapped_column(Integer, nullable=False, default=200)

    user: Mapped["User"] = relationship(back_populates="goals")
