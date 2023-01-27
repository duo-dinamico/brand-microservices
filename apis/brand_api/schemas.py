from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Extra, Field

from .db.models import MyEnum


class BrandsBase(BaseModel):
    name: str
    website: str
    category_id: UUID
    description: str
    average_price: str
    rating: int

    class Config:
        orm_mode = True


class BrandsResponse(BrandsBase):
    id: UUID

    class Config:
        orm_mode = True


class BrandsBaseOptionalBody(BaseModel):
    name: str | None
    website: str | None
    category_id: UUID | None
    description: str | None
    average_price: str | None
    rating: int | None

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: UUID
    email: str


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = ""
    exp: int = 0


class SystemUser(UserOut):
    password: str


class UserPasswordUpdate(BaseModel):
    password: str = Field(..., min_length=5, max_length=24, description="user password")

    class Config:
        extra = Extra.forbid


class CategoriesBase(BaseModel):
    name: str
    description: str
    price_per_category: MyEnum
    created_at: datetime
    created_by: UUID
    updated_at: datetime | None
    updated_by: UUID | None
    deleted_at: datetime | None
    deleted_by: UUID | None

    class Config:
        orm_mode = True


class CategoriesResponse(CategoriesBase):
    id: UUID

    class Config:
        orm_mode = True


class CategoriesBaseOptionalBody(BaseModel):
    name: str | None
    description: str | None
    price_per_category: MyEnum | None
    created_by: UUID | None

    class Config:
        orm_mode = True
