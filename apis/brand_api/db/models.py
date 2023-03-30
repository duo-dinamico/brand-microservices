from datetime import datetime
from enum import Enum as pyEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(unique=True)


class Social(Base):
    __tablename__ = "socials"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(unique=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[Optional[str]] = mapped_column(unique=True)
    password: Mapped[str]
    role_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("roles.id"))

    updated_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_updated_by"), default=None
    )
    updated_by: Mapped["User"] = relationship("User", primaryjoin="User.id==remote(User.updated_by_id)", uselist=False)
    deleted_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_deleted_by"), default=None
    )
    deleted_by: Mapped["User"] = relationship("User", primaryjoin="User.id==remote(User.deleted_by_id)", uselist=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(unique=True)

    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", name="users_id_created_by"))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_updated_by"), default=None
    )
    deleted_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_deleted_by"), default=None
    )

    created_by: Mapped["User"] = relationship("User", backref="categories_created_by", foreign_keys=[created_by_id])
    updated_by: Mapped["User"] = relationship("User", backref="categories_updated_by", foreign_keys=[updated_by_id])
    deleted_by: Mapped["User"] = relationship("User", backref="categories_deleted_by", foreign_keys=[deleted_by_id])

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)


class AveragePrice(int, pyEnum):
    low = 1
    medium = 2
    high = 3


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"))
    description: Mapped[Optional[str]]
    average_price: Mapped[Optional[pyEnum]] = mapped_column(Enum(AveragePrice))

    category: Mapped["Category"] = relationship("Category", backref="brands")

    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", name="users_id_created_by"))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_updated_by"), default=None
    )
    deleted_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_deleted_by"), default=None
    )

    created_by: Mapped["User"] = relationship("User", backref="brands_created_by", foreign_keys=[created_by_id])
    updated_by: Mapped["User"] = relationship("User", backref="brands_updated_by", foreign_keys=[updated_by_id])
    deleted_by: Mapped["User"] = relationship("User", backref="brands_deleted_by", foreign_keys=[deleted_by_id])

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)


class BrandSocial(Base):
    __tablename__ = "brands_socials"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand_id: Mapped[UUID] = mapped_column(ForeignKey("brands.id"))
    brand: Mapped["Brand"] = relationship("Brand", backref="brands_socials_brand", foreign_keys=[brand_id])
    social_id: Mapped[UUID] = mapped_column(ForeignKey("socials.id"))
    social: Mapped["Social"] = relationship("Social", backref="brands_socials_social", foreign_keys=[social_id])
    UniqueConstraint("brand_id", "social_id", name="brand_social")
    address: Mapped[str] = mapped_column(unique=True)

    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", name="users_id_created_by"))
    updated_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_updated_by"), default=None
    )
    deleted_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", name="users_id_deleted_by"), default=None
    )

    created_by: Mapped["User"] = relationship("User", backref="brands_socials_created_by", foreign_keys=[created_by_id])
    updated_by: Mapped["User"] = relationship("User", backref="brands_socials_updated_by", foreign_keys=[updated_by_id])
    deleted_by: Mapped["User"] = relationship("User", backref="brands_socials_deleted_by", foreign_keys=[deleted_by_id])

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)
