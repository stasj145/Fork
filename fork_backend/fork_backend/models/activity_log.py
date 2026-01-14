"""Data model to log all days where activities are performed"""
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base


class ActivityLog(Base):
    """The log of all dates where activities are performed"""
    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(Date, nullable=False, index=True)
    goals_id: Mapped[str] = mapped_column(String(36), ForeignKey("goals.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="activity_log")
    activity_entries: Mapped[list["ActivityEntry"]] = relationship(
        back_populates="activity_log", cascade="all, delete-orphan")

    goals: Mapped["Goals"] = relationship(foreign_keys=[goals_id])
