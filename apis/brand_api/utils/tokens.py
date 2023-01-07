import os
from datetime import datetime, timedelta
from typing import Any

from jose import jwt


def create_access_token(subject: str | Any, expires_delta: timedelta | Any = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=float(str(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))))

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, os.environ.get("JWT_SECRET_KEY"), os.environ.get("ALGORITHM"))
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: timedelta | Any = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=float(str(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES")))
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, os.environ.get("JWT_REFRESH_SECRET_KEY"), os.environ.get("ALGORITHM"))
    return encoded_jwt
