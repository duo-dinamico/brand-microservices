from datetime import datetime
from re import search
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field, StrictStr, root_validator, validator

from .db.models import AveragePrice


class UserBase(BaseModel):
    id: UUID
    username: str
    # For testing only
    info: Optional[str]

    class Config:
        orm_mode = True


class CategoriesBase(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class BrandsBase(BaseModel):
    id: UUID
    name: str
    category: CategoriesBase
    description: str | None
    average_price: AveragePrice
    line_address_1: str | None
    line_address_2: str | None
    city: str | None
    postal_code: str | None

    class Config:
        orm_mode = True


class SocialsBase(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class BrandSocialsBase(BaseModel):
    id: UUID
    brand: BrandsBase
    social: SocialsBase
    address: str

    class Config:
        orm_mode = True


class ListOfSocials(BaseModel):
    socials: List[SocialsBase]


class SocialsPostBody(BaseModel):
    name: StrictStr = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "Website",
            }
        }
        orm_mode = True
        extra = Extra.forbid


class BrandSocialsResponse(BrandSocialsBase):
    created_at: datetime
    created_by: UserBase
    updated_at: datetime | None
    updated_by: UserBase | None
    deleted_at: datetime | None
    deleted_by: UserBase | None

    class Config:
        orm_mode = True


class ListOfBrandSocials(BaseModel):
    socials: List[BrandSocialsResponse]


class BrandSocialsPostBody(BaseModel):
    social_id: UUID = Field(...)
    address: StrictStr = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "social_id": "dd57c7fd-a92f-42f1-891d-988803e4a878",
                "address": "www.website.com",
            }
        }
        orm_mode = True
        extra = Extra.forbid


class BrandSocialsPatchBody(BaseModel):
    social_id: Optional[UUID] = Field(default=None)
    address: Optional[StrictStr] = Field(default=None)

    class Config:
        schema_extra = {
            "example": {"social_id": "2162262c-2a94-4872-b862-0b42e03146c0", "address": "www.otherwebsite.com"}
        }
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True

    @root_validator(pre=True)
    def validate_xor(cls, values):
        if sum([bool(v) for v in values.values()]) < 1:
            raise ValueError("At least one of the keys social_id or address must exist.")
        return values


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

    class Config:
        schema_extra = {
            "example": {
                "name": "New Category",
            }
        }
        orm_mode = True
        extra = Extra.forbid


class CategoriesPatchBody(BaseModel):
    name: StrictStr

    class Config:
        schema_extra = {
            "example": {
                "name": "New Category",
            }
        }
        orm_mode = True
        extra = Extra.forbid


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
    category_id: UUID = Field(...)
    description: Optional[StrictStr] = Field(default=None)
    average_price: Optional[StrictStr] = Field(default=None)
    line_address_1: Optional[StrictStr] = Field(default=None)
    line_address_2: Optional[StrictStr] = Field(default=None)
    city: Optional[StrictStr] = Field(default=None)
    postal_code: Optional[StrictStr] = Field(default=None)

    @validator("postal_code")
    def validate_postal_code(cls, value):
        pattern = "^[0-9]{4}-[0-9]{3}$"
        if not bool(search(pattern, value)):
            raise ValueError("must correspond to the following format '0000-000'")
        return value

    class Config:
        schema_extra = {
            "example": {
                "name": "New Brand",
                "category_id": "95ae9f54-7d51-4ab5-a636-87b2d12921ef",
                "description": "This is an example of a new brand",
                "average_price": 2,
                "line_address_1": "22 Street",
                "line_address_2": "More street info",
                "city": "Porto",
                "postal_code": "4400-300",
            }
        }
        orm_mode = True
        extra = Extra.forbid


class BrandsPatchBody(BaseModel):
    name: Optional[StrictStr]
    category_id: Optional[UUID]
    description: Optional[StrictStr]
    average_price: Optional[StrictStr]
    line_address_1: Optional[StrictStr]
    line_address_2: Optional[StrictStr]
    city: Optional[StrictStr]
    postal_code: Optional[StrictStr]

    @validator("postal_code")
    def validate_postal_code(cls, value):
        pattern = "^[0-9]{4}-[0-9]{3}$"
        if not bool(search(pattern, value)):
            raise ValueError("must correspond to the following format '0000-000'")
        return value

    class Config:
        schema_extra = {
            "example": {
                "name": "New Brand",
                "category_id": "95ae9f54-7d51-4ab5-a636-87b2d12921ef",
                "description": "This is an example of a new brand",
                "average_price": 3,
                "line_address_1": "22 Street",
                "line_address_2": "More street info",
                "city": "Porto",
                "postal_code": "4400-300",
            }
        }
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True

    @root_validator(pre=True)
    def validate_xor(cls, values):
        if sum([bool(v) for v in values.values()]) < 1:
            raise ValueError("A minimum of 1 value will be required to do the update")
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
    role_id: Optional[UUID] = Field(default=None, description="User role UUID")
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
        if sum([bool(v) for v in values.values()]) < 1:
            raise ValueError("At least one of the keys email or password must exist.")
        return values


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = ""
    exp: int = 0


class Error400(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Bad request, data already exists",
            }
        }


class Error404(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Item not found",
            }
        }


class Error405(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Not authenticated",
            }
        }
