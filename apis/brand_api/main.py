from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .crud import (
    create_brand,
    create_category,
    create_user,
    crud_delete_brand,
    crud_delete_category,
    crud_delete_user,
    read_all_brands,
    read_all_categories,
    read_all_users,
    read_brand,
    read_category,
    read_user,
    update_brand,
    update_category,
    update_user,
)
from .db.database import SessionLocal, engine
from .db.models import Base
from .dependencies import get_current_user
from .schemas import (
    BrandsBase,
    BrandsBaseOptionalBody,
    BrandsResponse,
    CategoriesBaseOptionalBody,
    CategoriesResponse,
    SystemUser,
    TokenSchema,
    UserAuth,
    UserOut,
    UserPasswordUpdate,
)
from .utils.password_hash import get_hashed_password, verify_password
from .utils.tokens import create_access_token, create_refresh_token

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", status_code=405)
def read_root():
    pass


@app.post(
    "/brands",
    summary="Create new brand",
    response_model=BrandsResponse,
    status_code=201,
    dependencies=[Depends(get_current_user)],
    tags=["Brands"],
)
def post_brand(
    data: BrandsBase,
    db: Session = Depends(get_db),
):
    brand_name = read_brand(db, param={"name": data.name})
    brand_website = read_brand(db, param={"website": data.website})
    if brand_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand with this name already exists")
    if brand_website is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand with this website already exists")
    return create_brand(db, data)


@app.get("/brands", response_model=List[BrandsResponse], dependencies=[Depends(get_current_user)], tags=["Brands"])
def get_all_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brands = read_all_brands(db, skip=skip, limit=limit)
    return brands


@app.patch(
    "/brands/{brand_id}", response_model=BrandsResponse, dependencies=[Depends(get_current_user)], tags=["Brands"]
)
def patch_brand(
    data: BrandsBaseOptionalBody,
    brand_id: UUID = Path(title="The id of the brand to update"),
    db: Session = Depends(get_db),
):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "category_id":
            category = read_category(db, param={"id": value})
            if category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category must exist")
        setattr(brand, key, value)
    return update_brand(db, brand)


@app.delete("/brands/{brand_id}", dependencies=[Depends(get_current_user)], tags=["Brands"], status_code=204)
def delete_brand(brand_id: UUID = Path(title="The id of the brand to delete"), db: Session = Depends(get_db)):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return crud_delete_brand(db, brand)


@app.post(
    "/categories",
    summary="Create new category",
    response_model=CategoriesResponse,
    status_code=201,
    tags=["Categories"],
)
def post_category(
    data: CategoriesBaseOptionalBody,
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    setattr(data, "created_by", current_user.id)
    category_name = read_category(db, param={"name": data.name})
    if category_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with this name already exists")
    return create_category(db, data)


@app.get(
    "/categories",
    response_model=List[CategoriesResponse],
    dependencies=[Depends(get_current_user)],
    tags=["Categories"],
)
def get_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = read_all_categories(db, skip=skip, limit=limit)
    return categories


@app.patch(
    "/categories/{category_id}",
    response_model=CategoriesResponse,
    dependencies=[Depends(get_current_user)],
    tags=["Categories"],
)
def patch_category(
    data: CategoriesBaseOptionalBody,
    category_id: UUID = Path(title="The id of the category to update"),
    db: Session = Depends(get_db),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    return update_category(db, category)


@app.delete("/categories/{category_id}", dependencies=[Depends(get_current_user)], tags=["Categories"], status_code=204)
def delete_category(category_id: UUID = Path(title="The id of the category to delete"), db: Session = Depends(get_db)):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return crud_delete_category(db, category)


@app.patch("/users/{user_id}", dependencies=[Depends(get_current_user)], tags=["Users"])
def patch_user(
    data: UserPasswordUpdate, user_id: UUID = Path(title="User id to update"), db: Session = Depends(get_db)
):
    user = read_user(db, param={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    setattr(user, "password", get_hashed_password(data.password))
    return update_user(db, user)


@app.delete("/users/{user_id}", dependencies=[Depends(get_current_user)], tags=["Users"], status_code=204)
def delete_user(user_id: UUID = Path(title="The id of the user to delete"), db: Session = Depends(get_db)):
    user = read_user(db, param={"id": user_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return crud_delete_user(db, user)


@app.post("/signup", summary="Create new user", response_model=UserOut, status_code=201, tags=["Users"])
def post_user(data: UserAuth, db: Session = Depends(get_db)):
    user_check = read_user(db, param={"email": data.email})
    if user_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exist")
    user = {"email": data.email, "password": get_hashed_password(data.password)}
    user_created = create_user(db, user)
    # return {"id": user_created.id, "email": user_created.email}
    return user_created.__dict__


@app.post("/login", summary="Create access and refresh tokens for user", response_model=TokenSchema, tags=["Users"])
def post_login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = read_user(db, param={"email": form_data.username})
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password1")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password2")

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


@app.get(
    "/users",
    summary="Get details of all users",
    response_model=List[UserOut],
    dependencies=[Depends(get_current_user)],
    tags=["Users"],
)
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = read_all_users(db, skip=skip, limit=limit)
    return users
