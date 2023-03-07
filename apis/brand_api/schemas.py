from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field, StrictStr, root_validator

from .db.models import MyEnum


class TimestampAndOwnership(BaseModel):
    created_at: datetime
    created_by: UUID
    updated_at: datetime | None
    updated_by: UUID | None
    deleted_at: datetime | None
    deleted_by: UUID | None

    class Config:
        orm_mode = True


class CategoriesResponse(TimestampAndOwnership):
    id: UUID
    name: str
    description: str
    price_per_category: MyEnum

    class Config:
        orm_mode = True


class ListOfCategories(BaseModel):
    categories: List[CategoriesResponse]


class CategoriesPostBody(BaseModel):
    name: StrictStr = Field(...)
    description: Optional[StrictStr] = Field(default=None)
    price_per_category: MyEnum = Field(...)

    class Config:
        orm_mode = True
        extra = Extra.forbid


class CategoriesPatchBody(BaseModel):
    name: Optional[StrictStr] = Field(default=None)
    description: Optional[StrictStr] = Field(default=None)
    price_per_category: Optional[MyEnum] = Field(default=None)

    class Config:
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True

    @root_validator(pre=True)
    def validate_xor(cls, values):
        if sum([bool(v) for v in values.values()]) != 1:
            raise ValueError(f"At least one of the keys name, description or price_per_category must exist.")
        return values


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
    category: CategoriesResponse
    created_at: datetime
    created_by: UUID
    updated_at: datetime | None
    updated_by: UUID | None
    deleted_at: datetime | None
    deleted_by: UUID | None

    class Config:
        orm_mode = True


class ListOfBrands(BaseModel):
    brands: List[BrandsResponse]


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
    username: str
    created_at: datetime
    updated_at: datetime | None
    updated_by: UUID | None
    deleted_at: datetime | None
    deleted_by: UUID | None

    class Config:
        orm_mode = True


class UserEmail(UserOut):
    email: str | None


class ListOfUsers(BaseModel):
    users: List[UserOut]


class ListOfUsersWithEmail(BaseModel):
    users: List[UserEmail]


class UserAuth(BaseModel):
    username: str = Field(..., description="user name")
    email: str | None = Field(default=None, description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")

    class Config:
        extra = Extra.forbid


class SystemUser(UserOut):
    password: str


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, description="user email")
    password: str | None = Field(default=None, min_length=5, max_length=24, description="user password")

    class Config:
        extra = Extra.forbid


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = ""
    exp: int = 0
