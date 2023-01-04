from sqlalchemy.orm import Session

from .db.models import Brands, Users

# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()


def read_all_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Brands).offset(skip).limit(limit).all()


def read_user(db: Session, email):
    return db.query(Users).filter(Users.email == email).first()


def create_user(db: Session, user):
    db_user = Users(email=user["email"], password=user["password"])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user.user_data()


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
