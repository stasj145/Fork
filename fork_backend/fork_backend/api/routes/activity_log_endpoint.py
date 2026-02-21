"""Activity log management endpoints"""
# pylint: disable=raise-missing-from

from datetime import date as date_class
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import APIRouter, status, Depends, HTTPException, Path, Body, Query

from fork_backend.core.logging import get_logger
from fork_backend.api.dependencies import get_current_user
from fork_backend.api.schemas.activity_schema import (
    ActivityLogInDB, ActivityEntryInDB, ActivityEntryCreate, ActivityEntryUpdate)
from fork_backend.models.activity_log import ActivityLog
from fork_backend.models.user import User
from fork_backend.models.activity_entry import ActivityEntry
from fork_backend.services.activity_log_service import ActivityLogService

log = get_logger()
router = APIRouter(prefix="/log", tags=["Activity Log"])

@router.get("/day/{date}/activity", response_model=ActivityLogInDB, status_code=status.HTTP_200_OK)
async def get_or_create_activity_log(date: date_class = Path(...), user: User = Depends(get_current_user)):
    """
    Get the activity log for a specific day. Creates a new log, if that day has no log yet.
    """
    service = ActivityLogService()

    try:
        existing_log: ActivityLog = await service.get_log_by_date(user_id=user.id, log_date=date)
        if existing_log:
            return ActivityLogInDB.model_validate(existing_log)
        
        new_log: ActivityLog = await service.create_log(user_id=user.id, log_date=date)
        return ActivityLogInDB.model_validate(new_log)
    except SQLAlchemyError as sae:
        log.error(
            "Failed to get or create activity log for date '%s'. Unexpected SQLAlchemyError raised: %s", date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get or create activity log. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to get or create activity log for date '%s': %s", date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get or create activity log. Unexpected {str(type(e).__name__)} error raised",
        )

@router.post("/day/{date}/activity", response_model=ActivityEntryInDB, status_code=status.HTTP_201_CREATED)
async def add_activity_to_log(
    date: date_class = Path(...),
    activity_entry_data: ActivityEntryCreate = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Add an activity entry to a log for a specific date.
    
    :param date: The date of the log.
    :param activity_entry_data: The activity entry data to add.
    :param user: The currently logged in user.
    
    :return: The created activity entry.
    """
    service = ActivityLogService()
    
    try:
        activity_entry = ActivityEntry(
            activity_id=activity_entry_data.activity_id,
            duration=activity_entry_data.duration,
            calories_burned=activity_entry_data.calories_burned
        )
        
        created_entry = await service.add_activity_entry(
            user_id=user.id,
            log_date=date,
            activity_entry=activity_entry
        )
        
        return ActivityEntryInDB.model_validate(created_entry)
    except IntegrityError as ie:
        log.error(
            "Failed to add activity entry for date '%s'. IntegrityError raised: %s", date, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to add activity entry. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to add activity entry for date '%s'. Unexpected SQLAlchemyError raised: %s", date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add activity entry. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to add activity entry for date '%s': %s", date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add activity entry. Unexpected {str(type(e).__name__)} error raised",
        )

@router.delete("/day/{date}/activity/{activity_entry_id}", status_code=status.HTTP_200_OK)
async def remove_activity_entry(
    date: date_class = Path(...),
    activity_entry_id: str = Path(...),
    user: User = Depends(get_current_user)
):
    """
    Remove an activity entry from a log for a specific date.
    
    :param date: The date of the log.
    :param activity_entry_id: The ID of the activity entry to remove.
    :param user: The currently logged in user.
    
    :return: 204 No Content on successful deletion.
    """
    service = ActivityLogService()
    
    try:
        await service.remove_activity_entry(
            user_id=user.id,
            log_date=date,
            activity_entry_id=activity_entry_id
        )
        return
    except IntegrityError as ie:
        log.error(
            "Failed to remove activity entry '%s' for date '%s'. IntegrityError raised: %s", activity_entry_id, date, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to remove activity entry. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to remove activity entry '%s' for date '%s'. Unexpected SQLAlchemyError raised: %s", activity_entry_id, date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove activity entry. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to remove activity entry '%s' for date '%s': %s", activity_entry_id, date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove activity entry. Unexpected {str(type(e).__name__)} error raised",
        )

@router.patch("/day/{date}/activity/{activity_entry_id}", response_model=ActivityEntryInDB, status_code=status.HTTP_200_OK)
async def update_activity_entry(
    date: date_class = Path(...),
    activity_entry_id: str = Path(...),
    activity_entry_data: ActivityEntryUpdate = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Update an activity entry in a log for a specific date.
    Only duration and calories_burned can be updated.
    
    :param date: The date of the log.
    :param activity_entry_id: The ID of the activity entry to update.
    :param activity_entry_data: The activity entry data to update.
    :param user: The currently logged in user.
    
    :return: The updated activity entry.
    """
    service = ActivityLogService()
    
    try:
        updated_entry = await service.update_activity_entry(
            user_id=user.id,
            log_date=date,
            activity_entry_id=activity_entry_id,
            duration=activity_entry_data.duration,
            calories_burned=activity_entry_data.calories_burned
        )
        
        return ActivityEntryInDB.model_validate(updated_entry)
    except IntegrityError as ie:
        log.error(
            "Failed to update activity entry '%s' for date '%s'. IntegrityError raised: %s", activity_entry_id, date, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to update activity entry. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to update activity entry '%s' for date '%s'. Unexpected SQLAlchemyError raised: %s", activity_entry_id, date, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update activity entry. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to update activity entry '%s' for date '%s': %s", activity_entry_id, date, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update activity entry. Unexpected {str(type(e).__name__)} error raised",
        )

@router.get("/last/activity", response_model=list[ActivityLogInDB], status_code=status.HTTP_200_OK)
async def get_x_logs(n_logs: int = Query(1), user: User = Depends(get_current_user)):
    """
    Get the last x logs. Might be less if fewer are available
    :param n_logs: n_logs: How many logs to get. Starting with the latest available based on "date".
            0 to disable limit and get all (USE WITH CAUTION!).
    :param user: The currently logged in user.

    :return: List of ActivityLog with max length of n_logs. 
        (might be shorter if less entries are available)

    """
    service = ActivityLogService()

    try:
        last_logs: list[ActivityLog] = await service.get_last_x_logs(user_id=user.id, n_logs=n_logs)
        return [ActivityLogInDB.model_validate(log) for log in last_logs]
    except SQLAlchemyError as sae:
        log.error(
            "Failed to get last '%s' activity logs for user '%s'. Unexpected SQLAlchemyError raised: %s", n_logs, user.id, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get activity logs. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to get last '%s' activity logs for user '%s': %s", n_logs, user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity logs. Unexpected {str(type(e).__name__)} error raised",
        )
