from datetime import datetime
from enum import Enum
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import create_brand, read_all_brands, read_brand, read_category, update_brand
from ..db.database import SessionLocal
from ..dependencies import get_current_user
from . import brand_id_socials

router = APIRouter(prefix="/brands", tags=["Brands"])


class OrderBy(str, Enum):
    name = "name"
    average_price = "average_price"
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


@router.post(
    "/",
    response_model=schemas.ListOfBrands,
    summary="Create new brand",
    status_code=201,
)
def post_brand(
    data: schemas.BrandsPostBody,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    # TODO: Can we make these two only go to the DB once instead of twice?
    brand_name = read_brand(db, param={"name": data.name})
    category = read_category(db, param={"id": data.category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category must exist")
    if brand_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand with this name already exists")
    return {"brands": [create_brand(db, data, current_user.id)]}


@router.get("/", response_model=schemas.ListOfBrands, summary="List all brands")
def get_all_brands(
    skip: int = 0,
    limit: int = 100,
    show_deleted: bool = False,
    order_by: OrderBy = OrderBy.created_at,
    direction: OrderDirection = OrderDirection.asc,
    category_id: UUID = None,
    db: Session = Depends(get_db),
):
    return {
        "brands": read_all_brands(
            db,
            skip=skip,
            limit=limit,
            show_deleted=show_deleted,
            order_by=order_by,
            direction=direction,
            category_id=category_id,
        )
    }


@router.get(
    "/{brand_id}",
    response_model=schemas.ListOfBrands,
    summary="Fetch one brand by it's UUID",
)
def get_one_brand(
    brand_id: UUID = Path(title="The UUID of the brand to fetch"),
    show_deleted: bool = False,
    db: Session = Depends(get_db),
):
    brand = read_brand(db, param={"id": brand_id}, show_deleted=show_deleted)
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return {"brands": [read_brand(db, param={"id": brand_id}, show_deleted=show_deleted)]}


@router.patch("/{brand_id}", response_model=schemas.ListOfBrands, summary="Update a brand")
def patch_brand(
    data: schemas.BrandsPatchBody,
    brand_id: UUID = Path(title="The id of the brand to update"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by_id"] = current_user.id
    for key, value in update_data.items():
        if key == "category_id":
            category = read_category(db, param={"id": value})
            if category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category must exist")
        setattr(brand, key, value)
    return {"brands": [update_brand(db, brand)]}


@router.delete("/{brand_id}", response_model=schemas.ListOfBrands, summary="Delete a brand")
def delete_brand(
    brand_id: UUID = Path(title="The id of the brand to delete"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by_id": current_user.id}
    for key, value in deleted_dict.items():
        setattr(brand, key, value)
    return {"brands": [update_brand(db, brand)]}


router.include_router(brand_id_socials.router)
