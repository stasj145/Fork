"""goal model"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from fork_backend.models.base import Base

class System(Base):
    """User model"""
    __tablename__ = "system"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default="system")
    open_nutrition_data_import_started: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    open_nutrition_data_import_finished: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exercise_import_started: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exercise_import_finished: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
