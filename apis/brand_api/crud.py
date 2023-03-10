from datetime import datetime
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import schemas
from .db.models import Brand, Category, User


def create_brand(db: Session, brand: schemas.BrandsPostBody, user_id: UUID) -> Brand:
    db_brand = Brand(**brand.dict(), created_by_id=user_id)
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
            or_(Brand.deleted_at == None, Brand.deleted_at != None) if show_deleted else Brand.deleted_at == None,
        )
        .first()
    )


def read_all_brands(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[Brand]:
    return (
        db.query(Brand)
        .filter(or_(Brand.deleted_at == None, Brand.deleted_at != None) if show_deleted else Brand.deleted_at == None)
        .offset(skip)
        .limit(limit)
        .all()
    )


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


def read_all_categories(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[Category]:
    return (
        db.query(Category)
        .filter(
            or_(Category.deleted_at == None, Category.deleted_at != None)
            if show_deleted
            else Category.deleted_at == None
        )
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
            or_(Category.deleted_at == None, Category.deleted_at != None)
            if show_deleted
            else Category.deleted_at == None,
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
    return user


def read_user(db: Session, param: dict[str, str | UUID], show_deleted: bool = False) -> User:
    filtering_param = list(param.keys())[0]
    response = (
        db.query(User)
        .filter(
            getattr(User, filtering_param, None) == param.get(filtering_param),
            or_(User.deleted_at == None, User.deleted_at != None) if show_deleted else User.deleted_at == None,
        )
        .first()
    )

    if response != None:
        response_all = read_all_users(db, show_deleted=show_deleted)
        users_lookup: dict = {}
        for res in response_all:
            users_lookup[str(res.id)] = {"id": res.id, "username": res.username}
        if response.deleted_by_id != None:
            setattr(response, "deleted_by", users_lookup[str(res.deleted_by_id)])
        if response.updated_by_id != None:
            setattr(response, "updated_by", users_lookup[str(res.updated_by_id)])

    return response


def create_user(db: Session, user) -> dict[str, str]:
    db_user = User(username=user["username"], email=user["email"], password=user["password"], created_at=datetime.now())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    test = db.query(User).filter(User.id == db_user.id).first()
    return test


def read_all_users(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False) -> list[dict[str, str]]:
    response = (
        db.query(User)
        .filter(or_(User.deleted_at == None, User.deleted_at != None) if show_deleted else User.deleted_at == None)
        .offset(skip)
        .limit(limit)
        .all()
    )

    if len(response) > 0:
        users_lookup: dict = {}
        for res in response:
            users_lookup[str(res.id)] = {"id": res.id, "username": res.username}

        for user in response:
            if user.deleted_by_id != None:
                setattr(user, "deleted_by", users_lookup[str(user.deleted_by_id)])
            if user.updated_by_id != None:
                setattr(user, "updated_by", users_lookup[str(user.updated_by_id)])

    return response
