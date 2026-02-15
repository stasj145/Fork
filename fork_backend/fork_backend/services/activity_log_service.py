"""Service class to manipulate activity logs"""

from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from fork_backend.core.db import get_async_db
from fork_backend.core.logging import get_logger
from fork_backend.models.activity_log import ActivityLog
from fork_backend.models.goals import Goals
from fork_backend.models.activity_entry import ActivityEntry

logger = get_logger()


class ActivityLogService:
    """Service to handle activity log management"""

    def __init__(self) -> None:
        """"""

    async def create_log(self, user_id: str, log_date: date) -> ActivityLog:
        """
        Create an activity log.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.

        :return: The new ActivityLog object.
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

                # Create a new ActivityLog instance
                activity_log = ActivityLog(
                    user_id=user_id,
                    date=log_date,
                    goals_id=goals.id
                )

                db.add(activity_log)
                await db.commit()
            logger.debug("New activity log for user '%s' and date '%s' created.",
                         activity_log.user_id, activity_log.date)
            return await self.get_log_by_id(activity_log.id)
        except Exception as e:
            logger.error("Failed to create new activity log: %s", str(e))
            raise e

    async def get_log_by_id(self, log_id: str) -> Optional[ActivityLog]:
        """
        Get an activity log by its ID.

        :param log_id: The ID of the log to retrieve.

        :return: The ActivityLog object if found, None otherwise.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(ActivityLog)
                    .where(ActivityLog.id == log_id)
                    .options(
                        selectinload(ActivityLog.activity_entries).selectinload(
                            ActivityEntry.activity),
                        selectinload(ActivityLog.goals)
                    )
                )
                activity_log = result.scalar_one_or_none()
                return activity_log
        except Exception as e:
            logger.error("Failed to get activity log by ID '%s': %s", log_id, str(e))
            raise e

    async def get_log_by_date(self, user_id: str, log_date: date) -> Optional[ActivityLog]:
        """
        Get an activity log by user ID and date.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.

        :return: The ActivityLog object if found, None otherwise.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(ActivityLog)
                    .where(ActivityLog.user_id == user_id, ActivityLog.date == log_date)
                    .options(
                        selectinload(ActivityLog.activity_entries).selectinload(
                            ActivityEntry.activity),
                        selectinload(ActivityLog.goals)
                    )
                )
                activity_log = result.scalar_one_or_none()
                return activity_log
        except Exception as e:
            logger.error("Failed to get activity log for user '%s' and date '%s': %s", user_id, log_date,
                         str(e))
            raise e
        
    async def get_last_x_logs(self, user_id: str, n_logs: int) -> list[ActivityLog]:
        """
        Get a list of ActivityLog

        :param user_id: The ID of the user.
        :param n_logs: How many logs to get. Starting with the latest available based on "date".
            0 to disable limit and get all (USE WITH CAUTION!).

        :return: List of ActivityLog with max length of n_logs.
            (might be shorter if less entries are available)
        """
        try:
            async with get_async_db() as db:
                stmt = select(
                    ActivityLog).where(ActivityLog.user_id == user_id).order_by(
                        ActivityLog.date.desc()).options(
                        selectinload(ActivityLog.activity_entries).selectinload(
                            ActivityEntry.activity),
                        selectinload(ActivityLog.goals)
                        )
                if n_logs > 0:
                    stmt = stmt.limit(n_logs)

                result = await db.execute(stmt)
                food_logs = result.scalars().all()
                return food_logs
        except Exception as e:
            logger.error("Failed to get activity logs for user '%s': %s", user_id, str(e))
            raise e

    async def add_activity_entry(self, user_id: str, log_date: date, activity_entry: ActivityEntry
                                 ) -> ActivityEntry:
        """
        Add an activity entry to a log for a specific date.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.
        :param activity_entry: The ActivityEntry object to add.

        :return: The ActivityEntry object with eagerly loaded activity.
        """
        try:
            async with get_async_db() as db:
                # Get or create the log for the specified date
                activity_log = await self.get_log_by_date(user_id, log_date)
                if not activity_log:
                    activity_log = await self.create_log(user_id, log_date)

                activity_entry.log_id = activity_log.id

                db.add(activity_entry)
                await db.commit()
                await db.refresh(activity_entry)

                result = await db.execute(
                    select(ActivityEntry)
                    .where(ActivityEntry.id == activity_entry.id)
                    .options(selectinload(ActivityEntry.activity))
                )
                loaded_activity_entry = result.scalar_one()

            logger.debug("New activity entry for log '%s' created.", activity_log.id)
            return loaded_activity_entry
        except Exception as e:
            logger.error("Failed to add activity entry: %s", str(e))
            raise e

    async def remove_activity_entry(self, user_id: str, log_date: date, activity_entry_id: str) -> bool:
        """
        Remove an activity entry from a log for a specific date.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.
        :param activity_entry_id: The ID of the activity entry to remove.

        :return: True if the activity entry was successfully removed, False otherwise.
        """
        try:
            async with get_async_db() as db:
                activity_log = await self.get_log_by_date(user_id, log_date)
                if not activity_log:
                    raise ValueError(
                        f"No log found for user {user_id} on date {log_date}")

                result = await db.execute(
                    select(ActivityEntry)
                    .where(ActivityEntry.id == activity_entry_id, ActivityEntry.log_id == activity_log.id)
                )
                activity_entry = result.scalar_one_or_none()

                if not activity_entry:
                    raise ValueError(
                        f"Activity entry {activity_entry_id} not found in log for date {log_date}")

                await db.delete(activity_entry)
                await db.commit()

            logger.debug("Activity entry '%s' removed from log '%s'.",
                         activity_entry_id, activity_log.id)
            return True
        except Exception as e:
            logger.error("Failed to remove activity entry: %s", str(e))
            raise e

    async def update_activity_entry(self, user_id: str, log_date: date, activity_entry_id: str,
                                    duration: Optional[float] = None,
                                    calories_burned: Optional[float] = None) -> ActivityEntry:
        """
        Update an activity entry in a log for a specific date.
        Only duration and calories_burned can be updated.

        :param user_id: The ID of the user.
        :param log_date: The date of the log.
        :param activity_entry_id: The ID of the activity entry to update.
        :param duration: The new duration in minutes (optional).
        :param calories_burned: The new calories burned value (optional).

        :return: The updated ActivityEntry object with eagerly loaded activity.
        """
        try:
            async with get_async_db() as db:
                activity_log = await self.get_log_by_date(user_id, log_date)
                if not activity_log:
                    raise ValueError(
                        f"No log found for user {user_id} on date {log_date}")

                result = await db.execute(
                    select(ActivityEntry)
                    .where(ActivityEntry.id == activity_entry_id, ActivityEntry.log_id == activity_log.id)
                )
                activity_entry = result.scalar_one_or_none()

                if not activity_entry:
                    raise ValueError(
                        f"Activity entry {activity_entry_id} not found in log for date {log_date}")

                if duration is not None:
                    activity_entry.duration = duration
                if calories_burned is not None:
                    activity_entry.calories_burned = calories_burned

                await db.commit()
                await db.refresh(activity_entry)

                result = await db.execute(
                    select(ActivityEntry)
                    .where(ActivityEntry.id == activity_entry.id)
                    .options(selectinload(ActivityEntry.activity))
                )

                loaded_activity_entry = result.scalar_one()

                logger.debug("Activity entry '%s' updated in log '%s'.", activity_entry_id, activity_log.id)
                return loaded_activity_entry
        except Exception as e:
            logger.error("Failed to update activity entry: %s", str(e))
            raise e
