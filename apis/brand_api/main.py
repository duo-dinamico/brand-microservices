from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .crud import (
    create_brand,
    create_category,
    create_user,
    read_all_brands,
    read_all_categories,
    read_all_users,
    read_brand,
    read_category,
    read_user,
)
from .db.database import SessionLocal, engine
from .db.models import Base
from .dependencies import get_current_user
from .schemas import BrandsBase, BrandsResponse, CategoriesBase, CategoriesResponse, TokenSchema, UserAuth, UserOut
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


@app.post(
    "/categories",
    summary="Create new category",
    response_model=CategoriesResponse,
    status_code=201,
    dependencies=[Depends(get_current_user)],
    tags=["Categories"],
)
def post_category(data: CategoriesBase, db: Session = Depends(get_db)):
    category_name = read_category(db, data.name)
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


@app.post("/signup", summary="Create new user", response_model=UserOut, status_code=201, tags=["Users"])
def post_user(data: UserAuth, db: Session = Depends(get_db)):
    user = read_user(db, email=data.email)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exist")
    user = {"email": data.email, "password": get_hashed_password(data.password)}
    return create_user(db, user)


@app.post("/login", summary="Create access and refresh tokens for user", response_model=TokenSchema, tags=["Users"])
def post_login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = read_user(db, email=form_data.username)
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


# @app.get("/users/me", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
