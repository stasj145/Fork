"""auth functions"""

from datetime import datetime, timedelta
from typing import Optional
from os import environ
import bcrypt
from jose import jwt



SECRET_KEY = environ.get("FORK_BACKEND_SECRET_KEY",
                         default="very_secret_key_here_change_this_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(plain_text_password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    :param: plain_text_password: The password to hash.
    :return: The salted and hashed password as a string.
    """
    if not plain_text_password:
        raise ValueError("Password cannot be empty")

    # bcrypt requires bytes, so we encode the string to utf-8
    password_bytes = plain_text_password.encode('utf-8')

    salt = bcrypt.gensalt(rounds=12)

    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password: str, stored_hash: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash.

    :param: plain_text_password: The password to check.
    :param: stored_hash: The hash stored in the database.

    :return: bool: True if the password matches, False otherwise.
    """
    if not plain_text_password or not stored_hash:
        return False

    password_bytes = plain_text_password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hash_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
