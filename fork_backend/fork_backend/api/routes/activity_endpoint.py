"""activity management endpoints"""

from uuid import uuid4

from fastapi import APIRouter, status, Depends, HTTPException

from fork_backend.core.logging import get_logger
from fork_backend.api.dependencies import get_current_user
from fork_backend.services.activity_service import ActivityService
from fork_backend.api.schemas.activity_schema import (ActivityDetailed, ActivityCreate, ActivityUpdate, ActivitySearch)
from fork_backend.models.activities import Activities
from fork_backend.models.user import User

log = get_logger()
router = APIRouter(prefix="/activity", tags=["Activity"])

def verify_ownership(action: str, user: User, activity: Activities) -> bool:
    """
    Verify if the user has the right to access an Activity

    :param action: The action the user is trying to perform. "access", "edit" or "delete"
    :param user: The currently logged in user.
    :param activity: The activity they are trying to access.

    :return: True if user is allowed to access/edit/delete.
    """
    if action == "edit" and user.id == activity.user_id:
        return True
    if action == "delete" and user.id == activity.user_id:
        return True
    if action == "access":
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to access. Wrong user.",
    )

# --- Endpoints ---

@router.post("/", response_model=ActivityDetailed, status_code=status.HTTP_201_CREATED)
async def create_activity(activity_info: ActivityCreate, user: User = Depends(get_current_user)):
    """
    Create a new activity.
    """
    service = ActivityService()

    try:
        activity = Activities(id=str(uuid4()), user_id=user.id, **activity_info.model_dump())
        new_activity: Activities = await service.add_activity(activity)
        return ActivityDetailed.model_validate(new_activity)
    except Exception as e:
        log.error("Failed to create new Activity: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create Activity: {str(e)}",
        ) from e


@router.patch("/{activity_id}", response_model=ActivityDetailed, status_code=status.HTTP_200_OK)
async def update_activity(activity_id: str, activity_info: ActivityUpdate,
                          current_user: User = Depends(get_current_user)) -> ActivityDetailed:
    """
    Update a specific activity by ID.
    """
    try:
        service = ActivityService()

        activity_to_update = await service.get_activity_by_id(activity_id)

        if not activity_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

        if not verify_ownership(action="edit", user=current_user, activity=activity_to_update):
            return None

        # Update only the fields that were provided
        update_data = activity_info.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(activity_to_update, field, value)

        updated_activity = await service.update_activity(activity_to_update)

        if not updated_activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

        log.debug("Updated info for activity with id '%s'", activity_id)
        return ActivityDetailed.model_validate(updated_activity)
    except HTTPException:
        raise
    except Exception as e:
        log.error("Failed to update activity with id '%s': %s", activity_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update activity: {str(e)}",
        ) from e


@router.get("/{activity_id}", response_model=ActivityDetailed, status_code=status.HTTP_200_OK)
async def get_activity(activity_id: str, current_user: User = Depends(get_current_user)) -> ActivityDetailed:
    """
    Get a specific activity by ID.
    """
    try:
        service = ActivityService()
        activity = await service.get_activity_by_id(activity_id)

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

        if not verify_ownership(action="access", user=current_user, activity=activity):
            return None

        return ActivityDetailed.model_validate(activity)
    except HTTPException:
        raise
    except Exception as e:
        log.error("Failed to get Activity with id '%s': %s", activity_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to find requested Activity: {str(e)}",
        ) from e

@router.post("/search", response_model=list[ActivityDetailed], status_code=status.HTTP_200_OK)
async def search_activities(query: ActivitySearch, user: User = Depends(get_current_user)):
    """
    Search for activities.
    """
    service = ActivityService()

    try:
        activities: list[Activities] = await service.search_activities(
            user_id=user.id,
            query=query.query,
            limit=query.limit
        )
        return [ActivityDetailed.model_validate(activity) for activity in activities]
    except Exception as e:
        log.error("Failed to search for Activities: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to search Activities: {str(e)}",
        ) from e


@router.delete("/{activity_id}", status_code=status.HTTP_200_OK)
async def delete_activity(activity_id: str, current_user: User = Depends(get_current_user)):
    """
    Delete a specific activity by ID.
    """
    try:
        service = ActivityService()
        activity = await service.get_activity_by_id(activity_id)

        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )

        if not verify_ownership(action="delete", user=current_user, activity=activity):
            return None

        success = await service.delete_activity(activity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        log.error("Failed to delete Activity with id '%s': %s", activity_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to delete activity: {str(e)}",
        ) from e
