"""Service class to manipulate food logs"""

from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fork_backend.core.db import get_async_db
from fork_backend.core.logging import get_logger
from fork_backend.models.food_log import FoodLog
from fork_backend.models.goals import Goals
from fork_backend.models.food_item import FoodItem, FoodItemIngredient
from fork_backend.models.food_entry import FoodEntry
from fork_backend.models.meal_type import MealType


logger = get_logger()


class LogService:
    """Service to handle log management"""

    def __init__(self) -> None:
        """"""

    async def create_log(self, user_id: str, log_date: date) -> FoodLog:
        """
        Create a log.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.

        :return: The new FoodLog object.
        """
        try:
            async with get_async_db() as db:
                # Get the user's most recent goals
                goals_result = await db.execute(
                    select(Goals)
                    .where(Goals.user_id == user_id)
                    .order_by(Goals.created_at.desc())
                )
                goals = goals_result.scalars().first()

                if not goals:
                    raise ValueError(f"No goals found for user {user_id}")

                # Create a new FoodLog instance
                food_log = FoodLog(
                    user_id=user_id,
                    date=log_date,
                    goals_id=goals.id
                )

                db.add(food_log)
                await db.commit()
            logger.debug("New log for user '%s' and date '%s' created.",
                         food_log.user_id, food_log.date)
            return await self.get_log_by_id(food_log.id)
        except Exception as e:
            logger.error("Failed to create new log: %s", str(e))
            raise e

    async def get_log_by_id(self, log_id: str) -> Optional[FoodLog]:
        """
        Get a log by its ID.

        :param log_id: The ID of the log to retrieve.

        :return: The FoodLog object if found, None otherwise.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(FoodLog)
                    .where(FoodLog.id == log_id)
                    .options(
                        selectinload(FoodLog.food_entries).selectinload(
                            FoodEntry.food_item).selectinload(FoodItem.ingredients).selectinload(
                                FoodItemIngredient.ingredient),
                        selectinload(FoodLog.goals)
                    )
                )
                food_log = result.scalar_one_or_none()
                return food_log
        except Exception as e:
            logger.error("Failed to get log by ID '%s': %s", log_id, str(e))
            raise e

    async def get_log_by_date(self, user_id: str, log_date: date) -> Optional[FoodLog]:
        """
        Get a log by user ID and date.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.

        :return: The FoodLog object if found, None otherwise.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(FoodLog)
                    .where(FoodLog.user_id == user_id, FoodLog.date == log_date)
                    .options(
                        selectinload(FoodLog.food_entries).selectinload(
                            FoodEntry.food_item).selectinload(FoodItem.ingredients).selectinload(
                                FoodItemIngredient.ingredient),
                        selectinload(FoodLog.goals)
                    )
                )
                food_log = result.scalar_one_or_none()
                return food_log
        except Exception as e:
            logger.error("Failed to get log for user '%s' and date '%s': %s", user_id, log_date,
                         str(e))
            raise e

    async def get_last_x_logs(self, user_id: str, n_logs: int) -> list[FoodLog]:
        """
        Get a list of food logs

        :param user_id: The ID of the user.
        :param n_logs: How many logs to get. Starting with the latest available based on "date".
            0 to disable limit and get all (USE WITH CAUTION!).

        :return: List of FoodLog with max length of n_logs.
            (might be shorter if less entries are available)
        """
        try:
            async with get_async_db() as db:
                stmt = select(
                    FoodLog).where(FoodLog.user_id == user_id).order_by(
                        FoodLog.date.desc()).options(
                        selectinload(FoodLog.food_entries).selectinload(
                            FoodEntry.food_item).selectinload(FoodItem.ingredients).selectinload(
                                FoodItemIngredient.ingredient),
                        selectinload(FoodLog.goals)
                    )
                if n_logs > 0:
                    stmt = stmt.limit(n_logs)

                result = await db.execute(stmt)
                food_logs = result.scalars().all()
                return food_logs
        except Exception as e:
            logger.error("Failed to get logs for user '%s': %s", user_id, str(e))
            raise e

    async def add_food_entry(self, user_id: str, log_date: date, food_entry: FoodEntry
                             ) -> FoodEntry:
        """
        Add a food entry to a log for a specific date.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.
        :param food_entry: The FoodEntry object to add.

        :return: The FoodEntry object with eagerly loaded food_item.
        """
        try:
            async with get_async_db() as db:
                # Get or create the log for the specified date
                food_log = await self.get_log_by_date(user_id, log_date)
                if not food_log:
                    food_log = await self.create_log(user_id, log_date)

                food_entry.log_id = food_log.id

                db.add(food_entry)
                await db.commit()
                await db.refresh(food_entry)

                result = await db.execute(
                    select(FoodEntry)
                    .where(FoodEntry.id == food_entry.id)
                    .options(
                        selectinload(FoodEntry.food_item).selectinload(FoodItem.ingredients
                        ).selectinload(FoodItemIngredient.ingredient))
                )
                loaded_food_entry = result.scalar_one()

            logger.debug("New food entry for log '%s' created.", food_log.id)
            return loaded_food_entry
        except Exception as e:
            logger.error("Failed to add food entry: %s", str(e))
            raise e

    async def remove_food_entry(self, user_id: str, log_date: date, food_entry_id: str) -> bool:
        """
        Remove a food entry from a log for a specific date.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.
        :param food_entry_id: The ID of the food entry to remove.

        :return: True if the food entry was successfully removed, False otherwise.
        """
        try:
            async with get_async_db() as db:
                food_log = await self.get_log_by_date(user_id, log_date)
                if not food_log:
                    raise ValueError(
                        f"No log found for user {user_id} on date {log_date}")

                result = await db.execute(
                    select(FoodEntry)
                    .where(FoodEntry.id == food_entry_id, FoodEntry.log_id == food_log.id)
                )
                food_entry = result.scalar_one_or_none()

                if not food_entry:
                    raise ValueError(
                        f"Food entry {food_entry_id} not found in log for date {log_date}")

                await db.delete(food_entry)
                await db.commit()

            logger.debug("Food entry '%s' removed from log '%s'.",
                         food_entry_id, food_log.id)
            return True
        except Exception as e:
            logger.error("Failed to remove food entry: %s", str(e))
            raise e

    async def update_food_entry(self, user_id: str, log_date: date, food_entry_id: str,
                                meal_type: Optional[MealType] = None,
                                quantity: Optional[float] = None) -> FoodEntry:
        """
        Update a food entry in a log for a specific date.
        Only meal_type and quantity can be updated.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.
        :param food_entry_id: The ID of the food entry to update.
        :param meal_type: The new meal type (optional).
        :param quantity: The new quantity (optional).

        :return: The updated FoodEntry object with eagerly loaded food_item.
        """
        try:
            async with get_async_db() as db:
                food_log = await self.get_log_by_date(user_id, log_date)
                if not food_log:
                    raise ValueError(
                        f"No log found for user {user_id} on date {log_date}")

                result = await db.execute(
                    select(FoodEntry)
                    .where(FoodEntry.id == food_entry_id, FoodEntry.log_id == food_log.id)
                )
                food_entry = result.scalar_one_or_none()

                if not food_entry:
                    raise ValueError(
                        f"Food entry {food_entry_id} not found in log for date {log_date}")

                if meal_type is not None:
                    food_entry.meal_type = meal_type
                if quantity is not None:
                    food_entry.quantity = quantity

                await db.commit()
                await db.refresh(food_entry)

                result = await db.execute(
                    select(FoodEntry)
                    .where(FoodEntry.id == food_entry.id)
                    .options(
                        selectinload(FoodEntry.food_item).selectinload(FoodItem.ingredients
                            ).selectinload(FoodItemIngredient.ingredient))
                )

                loaded_food_entry = result.scalar_one()

                logger.debug("Food entry '%s' updated in log '%s'.", food_entry_id, food_log.id)
                return loaded_food_entry
        except Exception as e:
            logger.error("Failed to update food entry: %s", str(e))
            raise e
