from uuid import UUID

from pydantic import BaseModel, Field


class Brands(BaseModel):
    id: UUID
    name: str
    website: str
    category_id: UUID
    description: str
    average_price: str
    rating: int

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
