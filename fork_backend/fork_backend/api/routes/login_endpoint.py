"""API endpoint for logging in."""
# pylint: disable=raise-missing-from

from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from fork_backend.core.auth import create_access_token, verify_password
from fork_backend.core.logging import get_logger
from fork_backend.services.user_service import UserService

log = get_logger()
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to exchange username/password for an access token.
    Uses OAuth2PasswordRequestForm (application/x-www-form-urlencoded).
    """
    service = UserService()
    
    try:
        user = await service.get_user_by_username(form_data.username)
    except SQLAlchemyError as sae:
        log.error(
            "Failed to get user by username '%s'. Unexpected SQLAlchemyError raised: %s", form_data.username, str(sae))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user. Unexpected SQLAlchemyError raised",
        )
    except Exception as e:
        log.error("Failed to get user by username '%s': %s", form_data.username, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate user. Unexpected {str(type(e).__name__)} error raised",
        )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        access_token_expires = timedelta(days=7)
        access_token = create_access_token(
            data={"sub": user.id}, expires_delta=access_token_expires
        )
    except Exception as e:
        log.error("Failed to create access token for user '%s': %s", user.id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create access token. Unexpected {str(type(e).__name__)} error raised",
        )

    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}
