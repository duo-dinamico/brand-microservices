from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field, StrictInt, StrictStr, root_validator, validator

from .db.models import MyEnum


class UserBase(BaseModel):
    id: UUID
    username: str

    class Config:
        orm_mode = True


class CategoriesBase(BaseModel):
    id: UUID
    name: str
    description: str
    price_per_category: MyEnum

    class Config:
        orm_mode = True


class BrandsBase(BaseModel):
    id: UUID
    name: str
    website: str
    category: CategoriesBase
    description: str
    average_price: str
    rating: int

    class Config:
        orm_mode = True


class CategoriesResponse(CategoriesBase):
    created_at: datetime
    created_by: UserBase
    updated_at: datetime | None
    updated_by: UserBase | None
    deleted_at: datetime | None
    deleted_by: UserBase | None

    class Config:
        orm_mode = True


class ListOfCategories(BaseModel):
    categories: List[CategoriesResponse]


class CategoriesPostBody(BaseModel):
    name: StrictStr = Field(...)
    description: Optional[StrictStr] = Field(default=None)
    price_per_category: MyEnum = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "New Category",
                "description": "This is an example of a new category",
                "price_per_category": 3,
            }
        }
        orm_mode = True
        extra = Extra.forbid


class CategoriesPatchBody(BaseModel):
    name: Optional[StrictStr]
    description: Optional[StrictStr]
    price_per_category: Optional[MyEnum]

    class Config:
        schema_extra = {
            "example": {
                "name": "New Category",
                "description": "This is an example of a new category",
                "price_per_category": 3,
            }
        }
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True

    @root_validator(pre=True)
    def validate_xor(cls, values):
        if sum([bool(v) for v in values.values()]) != 1:
            raise ValueError("At least one of the keys name, description or price_per_category must exist.")
        return values


class BrandsResponse(BrandsBase):
    created_at: datetime
    created_by: UserBase
    updated_at: datetime | None
    updated_by: UserBase | None
    deleted_at: datetime | None
    deleted_by: UserBase | None

    class Config:
        orm_mode = True


class ListOfBrands(BaseModel):
    brands: List[BrandsResponse]


class BrandsPostBody(BaseModel):
    name: StrictStr = Field(...)
    website: Optional[StrictStr] = Field(default=None)
    category_id: UUID = Field(...)
    description: Optional[StrictStr] = Field(default=None)
    average_price: Optional[StrictStr] = Field(default=None)
    rating: Optional[StrictInt] = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "name": "New Brand",
                "website": "www.brand.pt",
                "category_id": "95ae9f54-7d51-4ab5-a636-87b2d12921ef",
                "description": "This is an example of a new brand",
                "average_price": "10$",
                "rating": 5,
            }
        }
        orm_mode = True
        extra = Extra.forbid


class BrandsPatchBody(BaseModel):
    name: Optional[StrictStr]
    website: Optional[StrictStr]
    category_id: Optional[UUID]
    description: Optional[StrictStr]
    average_price: Optional[StrictStr]
    rating: Optional[StrictInt]

    class Config:
        schema_extra = {
            "example": {
                "name": "New Brand",
                "website": "www.brand.pt",
                "category_id": "95ae9f54-7d51-4ab5-a636-87b2d12921ef",
                "description": "This is an example of a new brand",
                "average_price": "10$",
                "rating": 5,
            }
        }
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True

    @root_validator(pre=True)
    def validate_xor(cls, values):
        if sum([bool(v) for v in values.values()]) != 1:
            raise ValueError("At least one of the keys name or category_id must exist.")
        return values


class UserResponse(UserBase):
    created_at: datetime
    updated_at: datetime | None
    updated_by: UserBase | None = Field(default=None)
    deleted_at: datetime | None
    deleted_by: UserBase | None = Field(default=None)

    class Config:
        orm_mode = True


class UserResponseEmail(UserBase):
    email: Optional[str] = Field(default=None)
    created_at: datetime
    updated_at: datetime | None
    updated_by: UserBase | None
    deleted_at: datetime | None
    deleted_by: UserBase | None

    class Config:
        orm_mode = True


class UserResponsePassword(UserBase):
    password: str
    created_at: datetime
    updated_at: datetime | None
    updated_by: UserBase | None
    deleted_at: datetime | None
    deleted_by: UserBase | None


class ListOfUsers(BaseModel):
    users: List[UserResponse]


class ListOfUsersEmail(BaseModel):
    users: List[UserResponseEmail]


class UserPostBody(BaseModel):
    username: StrictStr = Field(..., min_length=5, max_length=16, description="User name")
    email: Optional[str] = Field(default=None, description="User email")
    password: str = Field(..., min_length=5, max_length=24, description="User password")

    @validator("password")
    def validate_password(cls, value):
        lower = 0
        upper = 0
        digits = 0
        for v in value:
            if v.islower():
                lower += 1
            elif v.isupper():
                upper += 1
            elif v.isdigit():
                digits += 1

        if lower == 0 or upper == 0 or digits == 0:
            raise ValueError("must contain at least 1 digit and 1 upper case.")

        return value

    class Config:
        schema_extra = {
            "example": {
                "username": "newUser",
                "email": "newemail@duodinamico.online",
                "password": "NewPassword1",
            }
        }
        orm_mode = True
        extra = Extra.forbid


class UserPatchBody(BaseModel):
    email: Optional[StrictStr] = Field(default=None, description="User email")
    password: Optional[str] = Field(default=None, min_length=5, max_length=24, description="User password")

    class Config:
        schema_extra = {
            "example": {
                "email": "newemail@duodinamico.online",
                "password": "NewPassword1",
            }
        }
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True

    @root_validator(pre=True)
    def validate_xor(cls, values):
        if sum([bool(v) for v in values.values()]) != 1:
            raise ValueError("At least one of the keys email or password must exist.")
        return values


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = ""
    exp: int = 0
