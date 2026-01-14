"""fastAPI Dependencies"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from fork_backend.services.user_service import UserService
from fork_backend.core.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["auth"])

# --- The Dependency ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency that decodes the token, fetches the user from the DB,
    and returns the User object.

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e
    
    service = UserService()
    user = await service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user