"""Model for all performed activities"""
from uuid import uuid4
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fork_backend.models.base import Base


class ActivityEntry(Base):
    """Model for all performed activities"""

    __tablename__ = "activity_entries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()))
    log_id: Mapped[str] = mapped_column(
        ForeignKey("activity_logs.id"), nullable=False)
    activity_id: Mapped[str] = mapped_column(String, ForeignKey("activities.id"), nullable=False)
    
    # Duration in minutes
    duration: Mapped[float] = mapped_column(
        Float, nullable=False)
        
    calories_burned: Mapped[float] = mapped_column(
        Float, nullable=True)

    # Relationships
    activity_log: Mapped["ActivityLog"] = relationship(back_populates="activity_entries")
    activity: Mapped["Activities"] = relationship(back_populates="activity_entries")
