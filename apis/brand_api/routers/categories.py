from datetime import datetime
from enum import Enum
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import create_category, read_all_categories, read_category, update_category
from ..db.database import SessionLocal
from ..dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


class OrderBy(str, Enum):
    name = "name"
    created_at = "created_at"
    updated_at = "updated_at"


class OrderDirection(str, Enum):
    asc = "asc"
    desc = "desc"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
def get_all_categories(
    skip: int = Query(default=0, description="Amount to offset the start of the query"),
    limit: int = Query(default=100, description="How many results to obtain per query"),
    show_deleted: bool = Query(default=False, description="Include deleted elements in the query"),
    order_by: OrderBy = OrderBy.created_at,
    direction: OrderDirection = OrderDirection.asc,
    db: Session = Depends(get_db),
):
    return {
        "categories": read_all_categories(
            db, skip=skip, limit=limit, show_deleted=show_deleted, order_by=order_by, direction=direction
        )
    }


@router.get(
    "/{category_id}",
    response_model=schemas.ListOfCategories,
    tags=["Categories"],
    summary="Retrieve a single category by it's UUID",
    responses={404: {"model": schemas.Error404}},
)
def get_category(
    category_id: UUID = Path(description="The id of the category"),
    show_deleted: bool = Query(default=False, description="Include deleted elements in the query"),
    db: Session = Depends(get_db),
):
    category = read_category(db, param={"id": category_id}, show_deleted=show_deleted)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"categories": [read_category(db, param={"id": category_id}, show_deleted=show_deleted)]}


@router.patch(
    "/{category_id}",
    response_model=schemas.ListOfCategories,
    tags=["Categories"],
    responses={404: {"model": schemas.Error404}, 405: {"model": schemas.Error405}},
)
def patch_category(
    data: schemas.CategoriesPatchBody,
    category_id: UUID = Path(description="The id of the category"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by_id"] = current_user.id
    for key, value in update_data.items():
        setattr(category, key, value)
    return {"categories": [update_category(db, category)]}


@router.delete(
    "/{category_id}",
    response_model=schemas.ListOfCategories,
    tags=["Categories"],
    responses={404: {"model": schemas.Error404}, 405: {"model": schemas.Error405}},
    description="The deletion is 'soft', it only adds a deleted_at and deleted_by to the Category",
)
def delete_category(
    category_id: UUID = Path(description="The id of the category"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by_id": current_user.id}
    for key, value in deleted_dict.items():
        setattr(category, key, value)
    return {"categories": [update_category(db, category)]}
