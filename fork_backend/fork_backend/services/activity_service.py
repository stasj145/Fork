"""Service class to manipulate activities"""

from typing import Optional, List
from sqlalchemy import select, and_

from fork_backend.core.db import get_async_db
from fork_backend.core.logging import get_logger
from fork_backend.models.activities import Activities

log = get_logger()


class ActivityService:
    """Service class for management of Activities.
    Other than with food, we only use simpler search logic without embeddings for now."""

    def __init__(self) -> None:
        """"""

    async def add_activity(self, activity: Activities) -> Activities:
        """
        Adds a new activity to the database.

        :param activity: The new activity to add.
        :return: The created Activities object.
        """
        try:
            async with get_async_db() as db:
                db.add(activity)
                await db.commit()
                log.debug("New activity added: %s", activity.name)
                return await self.get_activity_by_id(activity.id)

        except Exception as e:
            log.error("Failed to add activity from user '%s': %s",
                      activity.user_id, e)
            raise e

    async def update_activity(self, activity: Activities) -> Activities | None:
        """
        Update an existing activity's information.

        :param activity: The activity to update.
        :return: The updated Activities object.
        """
        try:
            async with get_async_db() as db:
                # Get original to check if it exists
                result = await db.execute(
                    select(Activities).filter(Activities.id == activity.id)
                )
                original = result.scalar_one_or_none()

                if not original:
                    log.error("Unable to find requested activity")
                    return None

                updated_activity = await db.merge(activity)
                await db.commit()

                log.debug("Updated Activity with id '%s'", activity.id)
                return await self.get_activity_by_id(updated_activity.id)

        except Exception as e:
            log.error("Failed to update activity with id '%s': %s",
                      activity.id, e)
            raise e

    async def get_activity_by_id(self, activity_id: str) -> Activities | None:
        """
        Get an Activity given its db id.

        :param activity_id: The id of the activity to get.
        :return: An instance of the Activities.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(Activities).filter(Activities.id == activity_id)
                )
                activity = result.scalar_one_or_none()
                return activity

        except Exception as e:
            log.error("Failed to get activity with id '%s': %s",
                      activity_id, e)
            raise e

    async def get_activities_by_user(self, user_id: str) -> List[Activities]:
        """
        Get all activities for a specific user.

        :param user_id: The id of the user.
        :return: A list of Activities.
        """
        try:
            async with get_async_db() as db:
                stmt = select(Activities).where(
                    Activities.user_id == user_id
                )

                result = await db.execute(stmt)
                activities = result.scalars().all()
                return activities

        except Exception as e:
            log.error("Failed to get activities for user '%s': %s", user_id, e)
            raise e

    async def search_activities(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: int = 20,
    ) -> List[Activities]:
        """
        Search for activities by name.

        :param user_id: The id of the user.
        :param query: The search query.
        :param limit: Maximum number of results to return.
        :return: A list of Activities matching the query.
        """
        try:
            if not query:
                return await self.get_activities_by_user(user_id)

            async with get_async_db() as db:
                stmt = select(Activities).where(
                    and_(
                        Activities.name.ilike(f"%{query}%")
                    )
                )

                stmt = stmt.limit(limit)

                result = await db.execute(stmt)
                activities = result.scalars().all()
                log.debug("Search for '%s' returned %d results", query, len(activities))
                return activities

        except Exception as e:
            log.error("Failed to search activities for query '%s': %s", query, e)
            raise e

    async def delete_activity(self, activity_id: str) -> bool:
        """
        Delete an activity from the database.

        :param activity_id: The ID of the activity to delete.
        :return: True if deletion was successful, False if item was not found.
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(Activities).filter(Activities.id == activity_id)
                )
                activity = result.scalar_one_or_none()

                if not activity:
                    log.warning(
                        "Unable to find activity with id '%s' for deletion", activity_id)
                    return False

                await db.delete(activity)
                await db.commit()
                log.debug("Deleted Activity with id '%s'", activity_id)
                return True

        except Exception as e:
            log.error("Failed to delete activity with id '%s': %s",
                      activity_id, e)
            raise e
