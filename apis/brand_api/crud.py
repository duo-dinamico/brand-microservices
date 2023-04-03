from datetime import datetime
from uuid import UUID

from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import Session

from . import schemas
from .db.models import Brand, BrandSocial, Category, Social, User
from .utils.logging import logger


def create_brand(db: Session, brand: schemas.BrandsPostBody, user_id: UUID) -> Brand:
    db_brand = Brand(**brand.dict(), created_by_id=user_id)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    logger.info(f"create_brand will return: {db_brand}")
    return db_brand


def read_brand(db: Session, param: dict[str, str | UUID], show_deleted: bool = False) -> Brand:
    filtering_param = list(param.keys())[0]
    return db.scalars(
        select(Brand).where(
            getattr(Brand, filtering_param, None) == param.get(filtering_param),
            or_(Brand.deleted_at == None, Brand.deleted_at != None) if show_deleted else Brand.deleted_at == None,
        )
    ).first()


def read_all_brands(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    show_deleted: bool = False,
    order_by: str = "created_at",
    direction: str = "asc",
    category_id: UUID = None,
) -> list[Brand]:
    filter_list = [
        or_(Brand.deleted_at == None, Brand.deleted_at != None) if show_deleted else Brand.deleted_at == None
    ]
    basequery = select(Brand).order_by(asc(order_by) if direction == "asc" else desc(order_by))
    if not category_id == None:
        filter_list.append(Brand.category_id == category_id)
    return db.scalars(basequery.where(*filter_list).offset(skip).limit(limit)).all()


def update_brand(db: Session, brand) -> Brand:
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def create_category(db: Session, category: schemas.CategoriesPostBody, user_id: UUID) -> Category:
    db_category = Category(
        **category.dict(),
        created_by_id=user_id,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def read_all_categories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    show_deleted: bool = False,
    order_by: str = "created_at",
    direction: str = "asc",
) -> list[Category]:
    return db.scalars(
        select(Category)
        .order_by(asc(order_by) if direction == "asc" else desc(order_by))
        .where(
            or_(Category.deleted_at == None, Category.deleted_at != None)
            if show_deleted
            else Category.deleted_at == None
        )
        .offset(skip)
        .limit(limit)
    ).all()


def read_category(db: Session, param, show_deleted: bool = False) -> Category:
    filtering_param = list(param.keys())[0]
    return db.scalars(
        select(Category).where(
            getattr(Category, filtering_param, None) == param.get(filtering_param),
            or_(Category.deleted_at == None, Category.deleted_at != None)
            if show_deleted
            else Category.deleted_at == None,
        )
    ).first()


def update_category(db: Session, category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_user(db: Session, user) -> dict[str, bool]:
    db.add(user)
    db.commit()
    db.refresh(user)
    return db.scalars(select(User).where(User.id == user.id)).first()


def read_user(db: Session, param: dict[str, str | UUID], show_deleted: bool = False) -> User:
    filtering_param = list(param.keys())[0]
    return db.scalars(
        select(User).where(
            getattr(User, filtering_param, None) == param.get(filtering_param),
            or_(User.deleted_at == None, User.deleted_at != None) if show_deleted else User.deleted_at == None,
        )
    ).first()


def create_user(db: Session, user) -> dict[str, str]:
    db_user = User(username=user["username"], email=user["email"], password=user["password"], created_at=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def read_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    show_deleted: bool = False,
    order_by: str = "created_at",
    direction: str = "asc",
) -> list[dict[str, str]]:
    return db.scalars(
        select(User)
        .order_by(asc(order_by) if direction == "asc" else desc(order_by))
        .where(or_(User.deleted_at == None, User.deleted_at != None) if show_deleted else User.deleted_at == None)
        .offset(skip)
        .limit(limit)
    ).all()


def read_social(db: Session, param: dict[str, str | UUID]) -> Social:
    filtering_param = list(param.keys())[0]
    return db.scalars(
        select(Social).where(getattr(Social, filtering_param, None) == param.get(filtering_param))
    ).first()


def create_social(db: Session, social: schemas.SocialsPostBody) -> Social:
    db_social = Social(**social.dict())
    db.add(db_social)
    db.commit()
    db.refresh(db_social)
    return db_social


def read_all_socials(db: Session, skip: int = 0, limit: int = 100) -> list[Social]:
    return db.scalars(select(Social).offset(skip).limit(limit)).all()


def create_brand_social(
    db: Session, brandsocial: schemas.BrandSocialsPostBody, brand_id: UUID, user_id: UUID
) -> BrandSocial:
    db_brandsocial = BrandSocial(**brandsocial.dict(), brand_id=brand_id, created_by_id=user_id)
    db.add(db_brandsocial)
    db.commit()
    db.refresh(db_brandsocial)
    return db_brandsocial


def read_all_brand_socials(
    db: Session, brand_id: UUID, skip: int = 0, limit: int = 100, show_deleted: bool = False
) -> list[BrandSocial]:
    return db.scalars(
        select(BrandSocial)
        .where(
            BrandSocial.brand_id == brand_id,
            or_(BrandSocial.deleted_at == None, BrandSocial.deleted_at != None)
            if show_deleted
            else BrandSocial.deleted_at == None,
        )
        .offset(skip)
        .limit(limit)
    ).all()


def read_brand_socials(db: Session, brand_socials_id: UUID, show_deleted: bool = False) -> list[BrandSocial]:
    return db.scalars(
        select(BrandSocial).where(
            BrandSocial.id == brand_socials_id,
            or_(BrandSocial.deleted_at == None, BrandSocial.deleted_at != None)
            if show_deleted
            else BrandSocial.deleted_at == None,
        )
    ).first()


def update_brand_socials(db: Session, brand_socials) -> BrandSocial:
    db.add(brand_socials)
    db.commit()
    db.refresh(brand_socials)
    return brand_socials
