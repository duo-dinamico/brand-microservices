from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class Brand(Base):
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True)
    website = Column(String, unique=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    description = Column(String)
    average_price = Column(String)
    rating = Column(Integer)

class MyEnum(enum.Enum):
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True)
    description = Column(String)
    price_per_category = Column(Enum(MyEnum))


