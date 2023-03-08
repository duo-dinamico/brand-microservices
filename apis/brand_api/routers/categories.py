from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import create_category, read_all_categories, read_category, update_category
from ..db.database import SessionLocal
from ..dependencies import get_current_user

router = APIRouter(prefix="/categories", dependencies=[Depends(get_current_user)], tags=["Categories"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def category_not_found(
    db: Session = Depends(get_db),
    category_id: UUID = Path(title="The ID of the category"),
    show_deleted: bool = Query(default=False),
):
    category = read_category(db, param={"id": category_id}, show_deleted=show_deleted)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category_id


@router.post(
    "/",
    summary="Create new category",
    response_model=schemas.ListOfCategories,
    status_code=201,
)
def post_category(
    data: schemas.CategoriesPostBody,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    category_name = read_category(db, param={"name": data.name})
    if category_name is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Category with this name already exists"
        )
    return {"categories": [create_category(db, data, current_user.id)]}


@router.get(
    "/",
    response_model=schemas.ListOfCategories,
    tags=["Categories"],
)
def get_all_categories(skip: int = 0, limit: int = 100, show_deleted: bool = False, db: Session = Depends(get_db)):
    return {"categories": read_all_categories(db, skip=skip, limit=limit, show_deleted=show_deleted)}


@router.get(
    "/{category_id}",
    response_model=schemas.ListOfCategories,
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
    summary="Retrieve a single category by it's UUID",
)
def get_category(
    category_id: UUID = Depends(category_not_found),
    show_deleted: bool = False,
    db: Session = Depends(get_db),
):
    return {"categories": [read_category(db, param={"id": category_id}, show_deleted=show_deleted)]}


@router.patch(
    "/{category_id}",
    response_model=schemas.ListOfCategories,
    tags=["Categories"],
)
def patch_category(
    data: schemas.CategoriesPatchBody,
    category_id: UUID = Depends(category_not_found),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user.id
    for key, value in update_data.items():
        setattr(category, key, value)
    return {"categories": [update_category(db, category)]}


@router.delete("/{category_id}", response_model=schemas.ListOfCategories, tags=["Categories"])
def delete_category(
    category_id: UUID = Depends(category_not_found),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by": current_user.id}
    for key, value in deleted_dict.items():
        setattr(category, key, value)
    return {"categories": [update_category(db, category)]}
