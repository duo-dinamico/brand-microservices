from uuid import UUID

from pydantic import BaseModel

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


# class UserCreate(UserBase):
#     password: str


class Brand(BaseModel):
    id: UUID
    name: str
    website: str
    category_id: UUID
    description: str
    average_price: str
    rating: int

    class Config:
        orm_mode = True
