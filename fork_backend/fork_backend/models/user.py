"""User model"""

from uuid import uuid4
from sqlalchemy import String, Float, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base
from fork_backend.models.activity_levels import ActivityLevels
from fork_backend.models.gender import Gender

class User(Base):
    """User model"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=85.4)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=180.0)
    age: Mapped[int] = mapped_column(Integer, nullable=False, default=18)
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender), nullable=False, default=Gender.MALE)
    activity_level: Mapped[ActivityLevels] = mapped_column(
        SQLEnum(ActivityLevels), nullable=False, default=ActivityLevels.SEDENTARY)

    food_log: Mapped[list["FoodLog"]] = relationship(back_populates="user",
                                                   cascade="all, delete-orphan")
    
    activity_log: Mapped[list["ActivityLog"]] = relationship(back_populates="user",
                                                           cascade="all, delete-orphan")
    
    goals: Mapped[list["Goals"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Goals.created_at.desc()"  # Most recent first
    )
