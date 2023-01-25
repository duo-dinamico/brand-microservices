import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates

from .database import Base


class Brands(Base):
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    website = Column(String, unique=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    description = Column(String)
    average_price = Column(String)
    rating = Column(Integer)

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", name="users_id_created_by"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", name="users_id_updated_by"), default=None)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", name="users_id_deleted_by"), default=None)

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=None)
    deleted_at = Column(DateTime, default=None)


class MyEnum(int, enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5


class Categories(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    description = Column(String)
    price_per_category = Column(Enum(MyEnum))

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", name="users_id_created_by"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", name="users_id_updated_by"), default=None)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", name="users_id_deleted_by"), default=None)

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=None)
    deleted_at = Column(DateTime, default=None)


class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    password = Column(String)

    updated_by = Column(UUID(as_uuid=True), default=None)
    deleted_by = Column(UUID(as_uuid=True), default=None)

    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=None)
    deleted_at = Column(DateTime, default=None)

    @validates("updated_by")
    def validate_user_id_exists(self, key, id):
        print("UUUUUUUUUUUUUUUUU", Users.query.filter(Users.id == id).first())
        if not Users.query.filter(Users.id == id).first():
            raise AssertionError("Updated_by user don't exist")
        return id
