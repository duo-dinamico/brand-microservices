from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ..crud import read_all_users, read_one_user, read_user, update_user
from ..db.database import SessionLocal
from ..dependencies import get_current_user
from ..schemas import ListOfUsers, ListOfUsersWithEmail, SystemUser, UserUpdate
from ..utils.password_hash import get_hashed_password

router = APIRouter(prefix="/users", dependencies=[Depends(get_current_user)], tags=["Users"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=ListOfUsers,
    summary="Get details of all users",
)
def get_all_users(skip: int = 0, limit: int = 100, show_deleted: bool = False, db: Session = Depends(get_db)):
    return {"users": read_all_users(db, skip=skip, limit=limit, show_deleted=show_deleted)}


@router.get(
    "/{user_id}",
    response_model=ListOfUsers,
    summary="Get details of all users",
)
def get_user(
    user_id: UUID = Path(title="User UUID to fetch"), show_deleted: bool = False, db: Session = Depends(get_db)
):
    user = read_user(db, param={"id": user_id}, show_deleted=show_deleted)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"users": [read_one_user(db, user_id, show_deleted=show_deleted)]}


@router.patch("/{user_id}", response_model=ListOfUsersWithEmail)
def patch_user(
    data: UserUpdate,
    user_id: UUID = Path(title="User UUID to update"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    user = read_user(db, param={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user.id
    for key, value in update_data.items():
        if key == "password":
            setattr(user, key, get_hashed_password(value))
        else:
            setattr(user, key, value)
    return {"users": [update_user(db, user)]}


@router.delete("/{user_id}", response_model=ListOfUsers)
def delete_user(
    user_id: UUID = Path(title="The id of the user to delete"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    user = read_user(db, param={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by": current_user.id}
    for key, value in deleted_dict.items():
        setattr(user, key, value)
    return {"users": [update_user(db, user)]}
