from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import (
    create_brand_social,
    read_all_brand_socials,
    read_brand,
    read_brand_socials,
    read_social,
    update_brand_socials,
)
from ..db.database import SessionLocal
from ..dependencies import get_current_user

router = APIRouter(prefix="/{brand_id}/socials", tags=["Brands"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=schemas.ListOfBrandSocials,
    summary="Post social adresses to a brand",
    status_code=201,
)
def post_brand_social(
    data: schemas.BrandSocialsPostBody,
    brand_id: UUID = Path(title="The UUID of the brand add socials to"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    # Path check
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand not found")
    # Body check
    social = read_social(db, param={"id": data.social_id})
    if social is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Social network not found")
    return {"socials": [create_brand_social(db, data, brand_id, current_user.id)]}


@router.get("/", response_model=schemas.ListOfBrandSocials, summary="List all socials pertaining to a brand")
def get_all_brand_socials(
    skip: int = 0,
    limit: int = 100,
    show_deleted: bool = False,
    brand_id: UUID = Path(title="The UUID of the brand add socials to"),
    db: Session = Depends(get_db),
):
    return {"socials": read_all_brand_socials(db, brand_id, skip=skip, limit=limit, show_deleted=show_deleted)}


@router.patch("/{brand_social_id}", response_model=schemas.ListOfBrandSocials, summary="Update the social of a brand")
def patch_brand_socials(
    data: schemas.BrandSocialsPatchBody,
    brand_id: UUID = Path(title="The id of the brand to update it's social"),
    brand_social_id: UUID = Path(title="The id of the brand's social"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    # Path
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    # Body
    brand_socials = read_brand_socials(db, brand_social_id)
    if brand_socials is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This social was not found associated with this brand"
        )
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by_id"] = current_user.id
    for key, value in update_data.items():
        if key == "social_id":
            social = read_social(db, param={"id": value})
            if social is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Social must exist.")
        setattr(brand_socials, key, value)
    return {"socials": [update_brand_socials(db, brand_socials)]}


@router.delete("/{brand_social_id}", response_model=schemas.ListOfBrandSocials, summary="Delete a social from a brand")
def delete_brand_socials(
    brand_id: UUID = Path(title="The id of the brand to delete a social from"),
    brand_social_id: UUID = Path(title="The id of the brand's social"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponsePassword = Depends(get_current_user),
):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    brand_socials = read_brand_socials(db, brand_social_id)
    if brand_socials is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="This social was not found associated with this brand"
        )
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by_id": current_user.id}
    for key, value in deleted_dict.items():
        setattr(brand_socials, key, value)
    response = update_brand_socials(db, brand_socials)
    return {"socials": [response]}
