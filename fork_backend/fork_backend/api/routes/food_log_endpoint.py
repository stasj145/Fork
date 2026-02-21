"""log management endpoints"""
# pylint: disable=raise-missing-from

from datetime import date as date_class
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import APIRouter, status, Depends, HTTPException, Path, Body, Query

from fork_backend.core.logging import get_logger
from fork_backend.api.dependencies import get_current_user
from fork_backend.api.schemas.log_schema import (
    LogInDB, FoodEntryInDB, FoodEntryCreate, FoodEntryUpdate)
from fork_backend.models.food_log import FoodLog
from fork_backend.models.user import User
from fork_backend.models.food_entry import FoodEntry
from fork_backend.services.food_log_service import LogService

log = get_logger()
router = APIRouter(prefix="/log", tags=["Food Log"])


@router.get("/day/{date}/food", response_model=LogInDB, status_code=status.HTTP_200_OK)
async def get_or_create_log(date: date_class = Path(...), user: User = Depends(get_current_user)):
    """
    Get the log for a specific day. Creates a new log, if that day has no log yet.
    """
    service = LogService()

    try:
        existing_log: FoodLog = await service.get_log_by_date(user_id=user.id, log_date=date)
        if existing_log:
            return LogInDB.model_validate(existing_log)

        new_log: FoodLog = await service.create_log(user_id=user.id, log_date=date)
        return LogInDB.model_validate(new_log)
    except SQLAlchemyError as sae:
        log.error(
            "Failed to get or create food log for date '%s'. Unexpected SQLAlchemyError raised: %s", date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create food log. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to get or create food log for date '%s': %s", date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get or create food log. Unexpected {str(type(e).__name__)} error raised",
        )

@router.post("/day/{date}/food", response_model=FoodEntryInDB, status_code=status.HTTP_201_CREATED)
async def add_food_to_log(
    date: date_class = Path(...),
    food_entry_data: FoodEntryCreate = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Add a food entry to a log for a specific date.

    :param date: The date of the log.
    :param food_entry_data: The food entry data to add.
    :param user: The currently logged in user.

    :return: The created food entry.
    """
    service = LogService()

    try:
        food_entry = FoodEntry(
            food_id=food_entry_data.food_id,
            quantity=food_entry_data.quantity,
            meal_type=food_entry_data.meal_type
        )

        created_entry = await service.add_food_entry(
            user_id=user.id,
            log_date=date,
            food_entry=food_entry
        )

        return FoodEntryInDB.model_validate(created_entry)
    except IntegrityError as ie:
        log.error(
            "Failed to add food entry for date '%s'. IntegrityError raised: %s", date, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to add food entry. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to add food entry for date '%s'. Unexpected SQLAlchemyError raised: %s", date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add food entry. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to add food entry for date '%s': %s", date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add food entry. Unexpected {str(type(e).__name__)} error raised",
        )


@router.delete("/day/{date}/food/{food_entry_id}", status_code=status.HTTP_200_OK)
async def remove_food_entry(
    date: date_class = Path(...),
    food_entry_id: str = Path(...),
    user: User = Depends(get_current_user)
):
    """
    Remove a food entry from a log for a specific date.

    :param date: The date of the log.
    :param food_entry_id: The ID of the food entry to remove.
    :param user: The currently logged in user.

    :return: 204 No Content on successful deletion.
    """
    service = LogService()

    try:
        await service.remove_food_entry(
            user_id=user.id,
            log_date=date,
            food_entry_id=food_entry_id
        )
        return
    except IntegrityError as ie:
        log.error(
            "Failed to remove food entry '%s' for date '%s'. IntegrityError raised: %s", food_entry_id, date, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to remove food entry. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to remove food entry '%s' for date '%s'. Unexpected SQLAlchemyError raised: %s", food_entry_id, date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove food entry. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to remove food entry '%s' for date '%s': %s", food_entry_id, date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove food entry. Unexpected {str(type(e).__name__)} error raised",
        )


@router.patch("/day/{date}/food/{food_entry_id}", response_model=FoodEntryInDB, status_code=status.HTTP_200_OK)
async def update_food_entry(
    date: date_class = Path(...),
    food_entry_id: str = Path(...),
    food_entry_data: FoodEntryUpdate = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Update a food entry in a log for a specific date.
    Only meal_type and quantity can be updated.

    :param date: The date of the log.
    :param food_entry_id: The ID of the food entry to update.
    :param food_entry_data: The food entry data to update.
    :param user: The currently logged in user.

    :return: The updated food entry.
    """
    service = LogService()

    try:
        updated_entry = await service.update_food_entry(
            user_id=user.id,
            log_date=date,
            food_entry_id=food_entry_id,
            meal_type=food_entry_data.meal_type,
            quantity=food_entry_data.quantity
        )

        return FoodEntryInDB.model_validate(updated_entry)
    except IntegrityError as ie:
        log.error(
            "Failed to update food entry '%s' for date '%s'. IntegrityError raised: %s", food_entry_id, date, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to update food entry. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to update food entry '%s' for date '%s'. Unexpected SQLAlchemyError raised: %s", food_entry_id, date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update food entry. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to update food entry '%s' for date '%s': %s", food_entry_id, date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update food entry. Unexpected {str(type(e).__name__)} error raised",
        )

@router.get("/last/food", response_model=list[LogInDB], status_code=status.HTTP_200_OK)
async def get_x_logs(n_logs: int = Query(1), user: User = Depends(get_current_user)):
    """
    Get the last x logs. Might be less if fewer are available
    :param n_logs: n_logs: How many logs to get. Starting with the latest available based on "date".
            0 to disable limit and get all (USE WITH CAUTION!).
    :param user: The currently logged in user.

    :return: List of FoodLog with max length of n_logs. 
        (might be shorter if less entries are available)

    """
    service = LogService()

    try:
        last_logs: list[FoodLog] = await service.get_last_x_logs(user_id=user.id, n_logs=n_logs)
        return [LogInDB.model_validate(log) for log in last_logs]
    except SQLAlchemyError as sae:
        log.error(
            "Failed to get last '%s' food logs for user '%s'. Unexpected SQLAlchemyError raised: %s", n_logs, user.id, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get food logs. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to get last '%s' food logs for user '%s': %s", n_logs, user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get food logs. Unexpected {str(type(e).__name__)} error raised",
        )
