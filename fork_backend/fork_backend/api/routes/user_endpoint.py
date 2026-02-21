"""User management endpoints"""
# pylint: disable=raise-missing-from

import os
from datetime import date
from typing import Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import APIRouter, status, Depends, HTTPException, Query

from fork_backend.core.logging import get_logger
from fork_backend.api.dependencies import get_current_user
from fork_backend.models.user import User
from fork_backend.models.goals import Goals
from fork_backend.services.user_service import UserService
from fork_backend.api.schemas.user_schema import (
    UserInDB, GoalsBase, UserCreate, UserUpdate, WeigthHistory)

log = get_logger()
router = APIRouter(prefix="/user", tags=["User"])


def verify_user_id(user: User, user_id_to_access: str) -> bool:
    """
    Verify if the user id of the logged in user is the same as the id they are trying to access.

    :param user: The currently logged in user.
    :param user_id_to_change: The user id they are trying to access.

    :param: True if ids are the same.
    """
    if user.id == user_id_to_access:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unable to access. Worng user.",
    )

def str_to_bool(val: str) -> bool:
    """
    (Very) Basic function to turn a string into a bool.
    
    :param val: String value to check
    :type val: str
    :return: True/False
    :rtype: bool
    """
    return val.lower() in ("true")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_info: UserCreate):
    """
    Create a new user.
    """
    user_creation_disabled: bool = str_to_bool(
        os.environ.get("FORK_USER_CREATION_DISABLED", default="false"))
    if user_creation_disabled:
        log.warning("Tried to create new user, but user creation is disabled")
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=("Tried to create new user, but user creation is disabled. " +
                    "Please contact the server admin."),
        )

    service = UserService()

    try:
        new_user: User = await service.create_user(
            username=user_info.username,
            email=user_info.email,
            password=user_info.password,
        )
    except IntegrityError as ie:
        log.error(
            "Failed to create new user. IntegrityError raised: %s", str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create user. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to create new user. Unexpected SQLAlchemyError raised: %s", str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to create new user: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create user. Unexpected {str(type(e).__name__)} error raised",
        )

    # create initial goals
    goals: Goals = Goals(user_id = new_user.id, **user_info.goals.model_dump())
    try:
        await service.create_goals(goals = goals)
    except IntegrityError as ie:
        log.error(
            "Failed to create goals for user '%s'. IntegrityError raised: %s", new_user.id, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create user goals. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to create goals for user '%s'. Unexpected SQLAlchemyError raised: %s", new_user.id, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user goals. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to create goals for user '%s': %s", new_user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create user goals. Unexpected {str(type(e).__name__)} error raised",
        )


@router.patch("/{user_id}", response_model=UserInDB, status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user_info: UserUpdate,
                      weight_date_overwrite: Optional[date] = Query(
                          None,
                          examples=["2026-01-29"],
                          description=("Date on which the 'weight' should be logged." +
                                       " Defaults to today, but should optimally always be set" +
                                       " to avoid timezone problems. YYYY-MM-DD.")),
                      current_user: User = Depends(get_current_user)) -> UserInDB:
    """
    Update a specific user by ID.
    """
    if not verify_user_id(current_user, user_id):
        return None

    service = UserService()

    try:
        if weight_date_overwrite:
            updated_user = await service.update_user(
                user_id=user_id,
                values_to_update=user_info.model_dump(),
                weight_date_overwrite=weight_date_overwrite
            )
        else:
            updated_user = await service.update_user(
                user_id=user_id,
                values_to_update=user_info.model_dump()
            )
        log.debug("Updated info for user with id '%s'", user_id)

        ret_user = UserInDB.model_validate(updated_user)
        ret_user.goals = GoalsBase.model_validate(updated_user.goals[0])
        return ret_user
    except IntegrityError as ie:
        log.error(
            "Failed to update user '%s'. IntegrityError raised: %s", user_id, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update user. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to update user '%s'. Unexpected SQLAlchemyError raised: %s", user_id, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update user. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to update user '%s': %s", user_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update user. Unexpected {str(type(e).__name__)} error raised",
        )


@router.get("/{user_id}", response_model=UserInDB, status_code=status.HTTP_200_OK)
async def get_user(user_id: str, current_user: User = Depends(get_current_user)) -> UserInDB:
    """
    Get a specific user by ID.
    """
    if not verify_user_id(current_user, user_id):
        return None

    service = UserService()

    try:
        user = await service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        ret_user = UserInDB.model_validate(user)
        ret_user.goals = GoalsBase.model_validate(user.goals[0])
        return ret_user
    except SQLAlchemyError as sae:
        log.error(
            "Failed to get user '%s'. Unexpected SQLAlchemyError raised: %s", user_id, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to get user '%s': %s", user_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user. Unexpected {str(type(e).__name__)} error raised",
        )


@router.put("/{user_id}/weight-history", response_model=list[WeigthHistory], status_code=status.HTTP_200_OK)
async def update_weight_history(user_id: str,
                                weight_history_list: list[WeigthHistory],
                                current_user: User = Depends(get_current_user)):
    """
    Update the weight history for a specific user.
    This endpoint accepts a list of weight history objects and updates them based on ID.
    If an ID is missing from the provided list, the corresponding object will be deleted.
    """
    if not verify_user_id(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to access. Wrong user.",
        )

    service = UserService()

    try:
        updated_weight_history = await service.update_weight_history_list(
            user_id=user_id,
            weight_history_list=weight_history_list
        )
        return updated_weight_history
    except IntegrityError as ie:
        log.error(
            "Failed to update weight history for user '%s'. IntegrityError raised: %s", user_id, str(ie))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to update weight history. IntegrityError raised",
        )
    except SQLAlchemyError as sae:
        log.error(
            "Failed to update weight history for user '%s'. Unexpected SQLAlchemyError raised: %s", user_id, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weight history. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to update weight history for user '%s': %s", user_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update weight history. Unexpected {str(type(e).__name__)} error raised",
        )
