from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from . import schemas
from .db.models import Brand, Category, User


def create_brand(db: Session, brand: schemas.BrandsBase, user_id: UUID) -> Brand:
    db_brand = Brand(**brand.dict(), created_by=user_id)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def read_brand(db: Session, param: dict[str, str | UUID], show_deleted: bool = False) -> Brand:
    filtering_param = list(param.keys())[0]
    return (
        db.query(Brand)
        .filter(
            getattr(Brand, filtering_param, None) == param.get(filtering_param),
            Brand.deleted_at == None if not show_deleted else Brand.deleted_at != None,
        )
        .first()
    )


def read_all_brands(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[Brand]:
    return (
        db.query(Brand)
        .filter(Brand.deleted_at == None if not show_deleted else Brand.deleted_at != None)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_brand(db: Session, brand) -> Brand:
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def create_category(db: Session, category: schemas.CategoriesBase, user_id: UUID) -> Category:
    db_category = Category(
        **category.dict(),
        created_by=user_id,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def read_all_categories(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.deleted_at == None if not show_deleted else Category.deleted_at != None)
        .offset(skip)
        .limit(limit)
        .all()
    )


def read_category(db: Session, param, show_deleted: bool = False) -> Category:
    filtering_param = list(param.keys())[0]
    return (
        db.query(Category)
        .filter(
            getattr(Category, filtering_param, None) == param.get(filtering_param),
            Category.deleted_at == None if not show_deleted else Category.deleted_at != None,
        )
        .first()
    )


def update_category(db: Session, category) -> Category:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_user(db: Session, user) -> dict[str, bool]:
    db.add(user)
    db.commit()
    db.refresh(user)
    return db.query(User).filter(User.id == user.id).first()


def read_user(db: Session, param: dict[str, str | UUID], show_deleted: bool = False) -> User:
    filtering_param = list(param.keys())[0]
    return (
        db.query(User)
        .filter(
            getattr(User, filtering_param, None) == param.get(filtering_param),
            User.deleted_at == None if not show_deleted else User.deleted_at != None,
        )
        .first()
    )


def create_user(db: Session, user) -> dict[str, str]:
    db_user = User(username=user["username"], email=user["email"], password=user["password"], created_at=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    test = db.query(User).filter(User.id == db_user.id).first()
    return test


def read_all_users(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[dict[str, str]]:
    return (
        db.query(User)
        .filter(User.deleted_at == None if not show_deleted else User.deleted_at != None)
        .offset(skip)
        .limit(limit)
        .all()
    )


def read_one_user(db: Session, user_id, show_deleted: bool = False) -> dict[str, str]:
    return (
        db.query(User)
        .filter(User.id == user_id, User.deleted_at == None if not show_deleted else User.deleted_at != None)
        .first()
    )
