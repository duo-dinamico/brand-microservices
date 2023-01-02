from uuid import UUID

from pydantic import BaseModel, Field

# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


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


class UserBase(BaseModel):
    email: str


class UserOut(UserBase):
    id: UUID


class UserCreate(UserBase):
    password: str


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")
