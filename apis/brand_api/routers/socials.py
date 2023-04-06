from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import create_social, read_all_socials, read_social
from ..db.database import SessionLocal
from ..dependencies import get_current_user

router = APIRouter(prefix="/socials", dependencies=[Depends(get_current_user)], tags=["Socials"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=schemas.ListOfSocials,
    summary="Post a new social network.",
    status_code=201,
    include_in_schema=False,
)
def post_social(
    data: schemas.SocialsPostBody,
    db: Session = Depends(get_db),
):
    social_name = read_social(db, param={"name": data.name})
    if social_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Social with this name already exists")
    return {"socials": [create_social(db, data)]}


@router.get(
    "/",
    response_model=schemas.ListOfSocials,
    summary="Get all available social networks",
)
def get_all_socials(
    skip: int = Query(default=0, description="Amount to offset the start of the query"),
    limit: int = Query(default=100, description="How many results to obtain per query"),
    db: Session = Depends(get_db),
):
    return {"socials": read_all_socials(db, skip=skip, limit=limit)}
