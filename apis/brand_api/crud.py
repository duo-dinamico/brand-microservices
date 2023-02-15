from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from .db.models import Brands, Categories, Users
from .schemas import BrandsBase


def create_brand(db: Session, brand: BrandsBase, user_id) -> Brands:
    db_brand = Brands(
        name=brand.name,
        website=brand.website,
        description=brand.description,
        category_id=brand.category_id,
        average_price=brand.average_price,
        rating=brand.rating,
        created_by=user_id,
    )
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def read_brand(db: Session, param: dict[str, str | UUID]) -> Brands:
    filtering_param = list(param.keys())[0]
    return (
        db.query(Brands)
        .filter(getattr(Brands, filtering_param, None) == param.get(filtering_param), Brands.deleted_at == None)
        .first()
    )


def read_all_brands(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[Brands]:
    return (
        db.query(Brands)
        .filter(Brands.deleted_at == None if not show_deleted else Brands.deleted_at != None)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_brand(db: Session, brand) -> Brands:
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def create_category(db: Session, category, user_id) -> Categories:
    db_category = Categories(
        name=category.name,
        description=category.description,
        price_per_category=category.price_per_category,
        created_by=user_id,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def read_all_categories(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[Categories]:
    return (
        db.query(Categories)
        .filter(Categories.deleted_at == None if not show_deleted else Categories.deleted_at != None)
        .offset(skip)
        .limit(limit)
        .all()
    )


def read_category(db: Session, param) -> Categories:
    filtering_param = list(param.keys())[0]
    return (
        db.query(Categories)
        .filter(getattr(Categories, filtering_param, None) == param.get(filtering_param), Categories.deleted_at == None)
        .first()
    )


def update_category(db: Session, category) -> Categories:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_user(db: Session, user) -> dict[str, bool]:
    db.add(user)
    db.commit()
    db.refresh(user)
    return (
        db.query(
            Users.id,
            Users.email,
            Users.created_at,
            Users.updated_by,
            Users.updated_at,
            Users.deleted_by,
            Users.deleted_at,
        )
        .filter(Users.id == user.id)
        .first()
    )


def read_user(db: Session, param) -> Users:
    filtering_param = list(param.keys())[0]
    return (
        db.query(Users)
        .filter(getattr(Users, filtering_param, None) == param.get(filtering_param), Users.deleted_at == None)
        .first()
    )


def create_user(db: Session, user) -> dict[str, str]:
    db_user = Users(email=user["email"], password=user["password"], created_at=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # TODO: This kind of return should probably be it's own CRUD function
    return (
        db.query(
            Users.id,
            Users.email,
            Users.created_at,
            Users.updated_by,
            Users.updated_at,
            Users.deleted_by,
            Users.deleted_at,
        )
        .filter(Users.id == db_user.id)
        .first()
    )


def read_all_users(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[dict[str, str]]:
    return (
        db.query(
            Users.id,
            Users.email,
            Users.created_at,
            Users.updated_by,
            Users.updated_at,
            Users.deleted_by,
            Users.deleted_at,
        )
        .filter(Users.deleted_at == None if not show_deleted else Users.deleted_at != None)
        .offset(skip)
        .limit(limit)
        .all()
    )
