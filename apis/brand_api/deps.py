import os
from sqlalchemy.orm import Session

from typing import Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import jwt
from pydantic import ValidationError
from .db.schemas import TokenPayload, SystemUser
from .db.database import SessionLocal
from .db.models import Users

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(reuseable_oauth)) -> SystemUser:
    try:
        payload = jwt.decode(token, os.environ.get("JWT_SECRET_KEY"), algorithms=os.environ.get("ALGORITHM"))
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: Users = db.query(Users).filter(Users.email == token_data.sub).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return SystemUser(**user.user_data)
