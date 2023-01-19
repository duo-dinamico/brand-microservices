from uuid import UUID

from sqlalchemy.orm import Session

from .db.models import Brands, Categories, Users
from .schemas import BrandsBase, BrandsResponse


def create_brand(db: Session, brand: BrandsBase) -> Brands:
    db_brand = Brands(
        name=brand.name,
        website=brand.website,
        description=brand.description,
        category_id=brand.category_id,
        average_price=brand.average_price,
        rating=brand.rating,
    )
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def read_brand(db: Session, param: dict[str, str | UUID]) -> Brands:
    filtering_param = list(param.keys())[0]
    return db.query(Brands).filter(getattr(Brands, filtering_param, None) == param.get(filtering_param)).first()


def read_all_brands(db: Session, skip: int = 0, limit: int = 100) -> list[Brands]:
    return db.query(Brands).offset(skip).limit(limit).all()


def crud_delete_brand(db: Session, brand: BrandsResponse) -> dict[str, bool]:
    db.delete(brand)
    db.commit()
    return {"ok": True}


def create_category(db: Session, category) -> Categories:
    db_category = Categories(
        name=category.name, description=category.description, price_per_category=category.price_per_category
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def read_all_categories(db: Session, skip: int = 0, limit: int = 100) -> list[Categories]:
    return db.query(Categories).offset(skip).limit(limit).all()


def read_category(db: Session, param) -> Categories:
    filtering_param = list(param.keys())[0]
    return db.query(Categories).filter(getattr(Categories, filtering_param, None) == param.get(filtering_param)).first()


def update_category(db: Session, category) -> Categories:
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def crud_delete_category(db: Session, category) -> dict[str, bool]:
    db.delete(category)
    db.commit()
    return {"ok": True}


def crud_delete_user(db: Session, user) -> dict[str, bool]:
    db.delete(user)
    db.commit()
    return {"ok": True}


def read_user(db: Session, param) -> Users:
    filtering_param = list(param.keys())[0]
    return db.query(Users).filter(getattr(Users, filtering_param, None) == param.get(filtering_param)).first()


def create_user(db: Session, user) -> dict[str, str]:
    db_user = Users(email=user["email"], password=user["password"])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.user_data


def read_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[dict[str, str]]:
    return db.query(Users.id, Users.email).offset(skip).limit(limit).all()


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
