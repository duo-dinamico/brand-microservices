from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ..crud import create_category, read_all_categories, read_category, update_category
from ..db.database import SessionLocal
from ..dependencies import get_current_user
from ..schemas import CategoriesBaseOptionalBody, ListOfCategories, SystemUser

router = APIRouter(prefix="/categories", dependencies=[Depends(get_current_user)], tags=["Categories"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    summary="Create new category",
    response_model=ListOfCategories,
    status_code=201,
)
def post_category(
    data: CategoriesBaseOptionalBody,
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    category_name = read_category(db, param={"name": data.name})
    if category_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with this name already exists")
    return {"categories": [create_category(db, data, current_user.id)]}


@router.get(
    "/",
    response_model=ListOfCategories,
    tags=["Categories"],
)
def get_all_categories(skip: int = 0, limit: int = 100, show_deleted: bool = False, db: Session = Depends(get_db)):
    return {"categories": read_all_categories(db, skip=skip, limit=limit, show_deleted=show_deleted)}


@router.get(
    "/{category_id}",
    response_model=ListOfCategories,
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
    summary="Retrieve a single category by it's UUID",
)
def get_category(
    category_id: UUID = Path(title="The UUID of the category to obtain"),
    show_deleted: bool = False,
    db: Session = Depends(get_db),
):
    category = read_category(db, param={"id": category_id}, show_deleted=show_deleted)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"categories": [read_category(db, param={"id": category_id}, show_deleted=show_deleted)]}


@router.patch(
    "/{category_id}",
    response_model=ListOfCategories,
    tags=["Categories"],
)
def patch_category(
    data: CategoriesBaseOptionalBody,
    category_id: UUID = Path(title="The id of the category to update"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user.id
    for key, value in update_data.items():
        setattr(category, key, value)
    return {"categories": [update_category(db, category)]}


@router.delete("/{category_id}", response_model=ListOfCategories, tags=["Categories"])
def delete_category(
    category_id: UUID = Path(title="The id of the category to delete"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by": current_user.id}
    for key, value in deleted_dict.items():
        setattr(category, key, value)
    return {"categories": [update_category(db, category)]}
