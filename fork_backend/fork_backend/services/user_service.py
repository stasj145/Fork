"""Service class to manipulate users"""

from typing import Any, Dict
from datetime import date
from sqlalchemy import update, select, inspect, desc
from sqlalchemy.orm import selectinload

from fork_backend.core.db import get_async_db
from fork_backend.core.auth import hash_password
from fork_backend.core.logging import get_logger
from fork_backend.models.user import User, WeigthHistory
from fork_backend.models.food_log import FoodLog
from fork_backend.models.goals import Goals
from fork_backend.models.activity_log import ActivityLog


log = get_logger()


class UserService:
    """Service to handle user management"""

    def __init__(self) -> None:
        """"""

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        """
        Create a new user.

        :param username: The name of the new user
        :param email: The email of the new user
        :param password: The clear-text pw.

        :return: The new user object.
        """
        try:
            new_user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
            )

            async with get_async_db() as db:
                db.add(new_user)
                await db.commit()
            log.debug("New user '%s' created.", username)
            return new_user
        except Exception as e:
            log.error("Failed to create new user: %s", str(e))
            raise e

    async def create_goals(
        self,
        goals: Goals,
    ) -> None:
        """
        Create new goals
        :param goals: The goals object to create.

        :return: The new goals object
        """
        try:
            async with get_async_db() as db:
                db.add(goals)
                await db.commit()
            log.debug("New goals '%s' created for user '%ss'.",
                      goals.id, goals.user_id)
        except Exception as e:
            log.error("Failed to create new goals: %s", str(e))
            raise e

    async def _update_food_log_goals(self, user_id: str) -> None:
        """
        Update the most recent food log's goals to point to the user's latest goals.

        :param user_id: The ID of the user whose food log goals to update
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(FoodLog)
                    .where(FoodLog.user_id == user_id)
                    .order_by(desc(FoodLog.date))
                    .limit(1)
                )
                most_recent_log = result.scalar_one_or_none()

                if not most_recent_log:
                    return

                new_goals_result = await db.execute(
                    select(Goals)
                    .where(Goals.user_id == user_id)
                    .order_by(desc(Goals.created_at))
                    .limit(1)
                )
                new_goals_obj = new_goals_result.scalar_one_or_none()

                if not new_goals_obj:
                    return

                most_recent_log.goals_id = new_goals_obj.id
                await db.commit()
                log.debug("Updated food log %s goals to new goals %s",
                          most_recent_log.id, new_goals_obj.id)

        except Exception as e:
            log.error("Failed to update food log goals: %s", str(e))

    async def _update_activity_log_goals(self, user_id: str) -> None:
        """
        Update the most recent activity log's goals to point to the user's latest goals.

        :param user_id: The ID of the user whose activity log goals to update
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(ActivityLog)
                    .where(ActivityLog.user_id == user_id)
                    .order_by(desc(ActivityLog.date))
                    .limit(1)
                )
                most_recent_log = result.scalar_one_or_none()

                if not most_recent_log:
                    return

                new_goals_result = await db.execute(
                    select(Goals)
                    .where(Goals.user_id == user_id)
                    .order_by(desc(Goals.created_at))
                    .limit(1)
                )
                new_goals_obj = new_goals_result.scalar_one_or_none()

                if not new_goals_obj:
                    return

                most_recent_log.goals_id = new_goals_obj.id
                await db.commit()
                log.debug("Updated activity log %s goals to new goals %s",
                          most_recent_log.id, new_goals_obj.id)

        except Exception as e:
            log.error("Failed to update activity log goals: %s", str(e))

    async def update_goals(
        self,
        user_id: str,
        new_goals: Dict[str, Any]
    ) -> None:
        """
        Update user goals only if they have actually changed.

        :param user_id: The ID of the user whose goals to update
        :param new_goals: The new goal values to set
        """
        user = await self.get_user_by_id(user_id)

        if not user.goals:
            await self.create_goals(Goals(user_id=user_id, **new_goals))
            return

        current_goals = user.goals[0]

        # Check if any goal values have actually changed
        has_changes = (
            new_goals.get("daily_calorie_target") != current_goals.daily_calorie_target or
            new_goals.get("daily_protein_target") != current_goals.daily_protein_target or
            new_goals.get("daily_carbs_target") != current_goals.daily_carbs_target or
            new_goals.get("daily_fat_target") != current_goals.daily_fat_target or
            new_goals.get(
                "daily_calorie_burn_target") != current_goals.daily_calorie_burn_target
        )

        if has_changes:
            await self.create_goals(Goals(user_id=user_id, **new_goals))
            await self._update_food_log_goals(user_id)
            await self._update_activity_log_goals(user_id)

    async def update_user(
        self,
        user_id: str,
        values_to_update: dict[str, Any],
        weight_date_overwrite: date = date.today(),
    ) -> User | None:
        """
        Update a users details.

        :param user_id: The ID of the user to update
        :param values_to_update: key-value pairs of which columns to update and with what value.
        :param weight_date_overwrite: Overwrite the date on which a weight change should be logged,
        defaults to date.today().

        :return: The updated user
        """

        filtered_updates: dict[str, Any] = {}

        # Update goals separately
        if "goals" in values_to_update.keys() and values_to_update["goals"] is not None:
            await self.update_goals(user_id, values_to_update["goals"])
            values_to_update = {k: v for k,
                                v in values_to_update.items() if k != "goals"}

        # Update weight history seperately
        if "weight" in values_to_update.keys() and values_to_update["weight"] is not None:
            await self.update_weight_history(weight_history_entry=WeigthHistory(
                user_id=user_id,
                weight=values_to_update["weight"],
                created_at=weight_date_overwrite
            ))
            values_to_update = {k: v for k,
                                v in values_to_update.items() if k != "weight"}

        try:
            async with get_async_db() as db:
                mapper = inspect(User)
                valid_columns = mapper.attrs.keys()

                # Filter the input to only include valid columns
                filtered_updates = {
                    k: v for k, v in values_to_update.items() if v is not None and k in valid_columns}

                # Update password
                if "password" in values_to_update.keys() and values_to_update["password"] is not None:
                    filtered_updates["hashed_password"] = hash_password(
                        values_to_update["password"])

                if not filtered_updates:
                    return await self.get_user_by_id(user_id)

                stmt = update(User).where(User.id == user_id).values(filtered_updates).returning(
                    User).options(selectinload(User.goals), selectinload(User.weight_history))

                result = await db.execute(stmt)
                await db.commit()

                user = result.scalar_one()
            log.debug("User %s updated.", user_id)
        except Exception as e:
            log.error("Failed to update user: %s", str(e))
            raise e
        return user

    async def get_user_by_id(self, user_id: str) -> User:
        """Get a user by id.

        :param user_id: the id of the user to get.

        :return: The User object
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(User).filter(User.id == user_id).options(selectinload(User.goals),
                                                                    selectinload(User.weight_history)))
                user = result.scalar_one_or_none()

                if user:
                    return user
                else:
                    log.error("Could not find user with id '%s'", user_id)
                    raise ValueError(
                        f"Could not find user with id '{user_id}'")
        except ValueError:
            raise
        except Exception as e:
            log.error("Failed to get user with id '%s': %s", user_id, str(e))
            raise e

    async def get_user_by_username(self, username: str) -> User:
        """Get a user by username.

        :param username: the username of the user to get.

        :return: The User object
        """
        try:
            async with get_async_db() as db:
                result = await db.execute(
                    select(User).filter(User.username == username).options(selectinload(User.goals),
                                                                           selectinload(User.weight_history)))
                user = result.scalar_one_or_none()

                if user:
                    return user
                else:
                    log.error(
                        "Could not find user with username '%s'", username)
                    raise ValueError(
                        f"Could not find user with username '{username}'"
                    )
        except ValueError:
            raise
        except Exception as e:
            log.error(
                "Failed to get user with username '%s': %s", username, str(e)
            )
            raise e

    async def update_weight_history(self, weight_history_entry: WeigthHistory) -> list[WeigthHistory]:
        """Update the weight history with either an entirely new entry or a changed existing entry"""
        user = await self.get_user_by_id(user_id=weight_history_entry.user_id)
        weight_history = user.weight_history

        async with get_async_db() as db:
            for existing_history_entry in weight_history:
                if existing_history_entry.id == weight_history_entry.id:
                    stmt = update(WeigthHistory).where(WeigthHistory.id == weight_history_entry.id).values(
                        {"weight": weight_history_entry.weight})
                    await db.execute(stmt)
                    await db.commit()
                    existing_history_entry.weight = weight_history_entry.weight
                    return weight_history

                if existing_history_entry.created_at == weight_history_entry.created_at:
                    stmt = update(WeigthHistory).where(WeigthHistory.created_at == weight_history_entry.created_at).values(
                        {"weight": weight_history_entry.weight})
                    await db.execute(stmt)
                    await db.commit()
                    existing_history_entry.weight = weight_history_entry.weight
                    return weight_history

            # if weight_history_entry id is not found in weight_history, add a new entry
            db.add(weight_history_entry)
            await db.commit()
            weight_history.insert(0, weight_history_entry)
        return weight_history

    async def update_weight_history_list(self, user_id: str, weight_history_list: list[WeigthHistory]) -> list[WeigthHistory]:
        """Update the weight history for a user with a list of weight history objects.
        If an ID is missing from the provided list, the corresponding object will be deleted.

        :param user_id: The id of the user to update
        :param weight_history_list: The history items to update with
        :return: The updated list, sorted with newest dates first
        """
        user = await self.get_user_by_id(user_id=user_id)
        existing_weight_history = user.weight_history

        incoming_ids = {entry.id for entry in weight_history_list if entry.id}

        # Delete entries that exist in the database but not in the incoming list
        async with get_async_db() as db:
            for existing_entry in existing_weight_history:
                if existing_entry.id not in incoming_ids:
                    # Remove missing entries
                    await db.delete(existing_entry)
                    await db.commit()
                    existing_weight_history.remove(existing_entry)

            for entry in weight_history_list:
                if entry.id:
                    existing_entry = next(
                        (e for e in existing_weight_history if e.id == entry.id), None)
                    if existing_entry:
                        # Update existing entry
                        existing_entry.weight = entry.weight
                        stmt = update(WeigthHistory).where(
                            WeigthHistory.id == entry.id).values({"weight": entry.weight, "created_at": entry.created_at})
                        await db.execute(stmt)
                        await db.commit()
                else:
                    # Create new entry
                    new_entry = WeigthHistory(
                        user_id=user_id,
                        weight=entry.weight,
                        created_at=entry.created_at
                    )
                    db.add(new_entry)
                    await db.commit()
                    existing_weight_history.append(new_entry)

        return sorted(existing_weight_history, key=lambda x: x.created_at, reverse=True)
