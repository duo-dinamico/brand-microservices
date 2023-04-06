from datetime import datetime
from enum import Enum
from os import getenv
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import read_all_users, read_user, update_user
from ..db.database import SessionLocal
from ..dependencies import get_current_user
from ..utils.password_hash import get_hashed_password

router = APIRouter(prefix="/users", dependencies=[Depends(get_current_user)], tags=["Users"])


class OrderBy(str, Enum):
    username = "username"
    email = "email"
    role_id = "role_id"
    created_at = "created_at"
    updated_at = "updated_at"


class OrderDirection(str, Enum):
    asc = "asc"
    desc = "desc"


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=schemas.ListOfUsers,
    summary="Get details of all users",
    responses={405: {"model": schemas.Error405}},
)
def get_all_users(
    skip: int = Query(default=0, description="Amount to offset the start of the query"),
    limit: int = Query(default=100, description="How many results to obtain per query"),
    show_deleted: bool = Query(default=False, description="Include deleted elements in the query"),
    order_by: OrderBy = OrderBy.created_at,
    direction: OrderDirection = OrderDirection.asc,
    db: Session = Depends(get_db),
):
    response = read_all_users(
        db, skip=skip, limit=limit, show_deleted=show_deleted, order_by=order_by.value, direction=direction
    )
    return {"users": response}


@router.get(
    "/{user_id}",
    response_model=schemas.ListOfUsers,
    summary="Get details of all users",
    responses={405: {"model": schemas.Error405}},
)
def get_user(
    user_id: UUID = Path(description="User id to fetch"),
    show_deleted: bool = Query(default=False, description="Include deleted elements in the query"),
    db: Session = Depends(get_db),
):
    user = read_user(db, param={"id": user_id}, show_deleted=show_deleted)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"users": [user]}


@router.patch(
    "/{user_id}",
    response_model=schemas.ListOfUsersEmail,
    summary="Update an user",
    responses={404: {"model": schemas.Error404}, 405: {"model": schemas.Error405}},
)
def patch_user(
    data: schemas.UserPatchBody,
    user_id: UUID = Path(description="The id of the user to update"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    user = read_user(db, param={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by_id"] = current_user.id
    for key, value in update_data.items():
        if key == "password":
            setattr(user, key, get_hashed_password(value))
        else:
            setattr(user, key, value)

    response = (
        update_user(db, user)
        if getenv("ENVIRONMENT") == "test"
        else {
            "id": uuid4(),
            "username": "trialUser",
            "created_at": datetime.now(),
            "info": "Patching the trial user is currently disabled in testing.",
        }
    )

    return {"users": [response]}


@router.delete(
    "/{user_id}",
    response_model=schemas.ListOfUsers,
    summary="Delete an user",
    description="The deletion is 'soft', it only adds a deleted_at and deleted_by to the User",
    responses={404: {"model": schemas.Error404}, 405: {"model": schemas.Error405}},
)
def delete_user(
    user_id: UUID = Path(description="The id of the user to delete"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    user = read_user(db, param={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    deleted_dict = {"deleted_at": datetime.now(), "deleted_by_id": current_user.id}
    for key, value in deleted_dict.items():
        setattr(user, key, value)

    response = (
        update_user(db, user)
        if getenv("ENVIRONMENT") == "test"
        else {
            "id": uuid4(),
            "username": "trialUser",
            "created_at": datetime.now(),
            "info": "Deleting the trial user is currently disabled in testing.",
        }
    )

    return {"users": [response]}
