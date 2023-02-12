from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .crud import (
    create_brand,
    create_category,
    create_user,
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
    CategoriesBaseOptionalBody,
    CategoriesResponse,
    ListOfBrands,
    SystemUser,
    TokenSchema,
    UserAuth,
    UserOut,
    UserPasswordUpdate,
)
from .utils.password_hash import get_hashed_password, verify_password
from .utils.tokens import create_access_token, create_refresh_token

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brands API", version="0.1.0")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", status_code=405, include_in_schema=False)
def read_root():
    pass


@app.post(
    "/brands",
    summary="Create new brand",
    response_model=ListOfBrands,
    status_code=201,
    tags=["Brands"],
)
def post_brand(
    data: BrandsBase,
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    # TODO: Can we make these two only go to the DB once instead of twice?
    brand_name = read_brand(db, param={"name": data.name})
    if brand_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand with this name already exists")
    brand_website = read_brand(db, param={"website": data.website})
    if brand_website is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Brand with this website already exists")
    return {"brands": [create_brand(db, data, current_user.id)]}


@app.get("/brands", response_model=ListOfBrands, dependencies=[Depends(get_current_user)], tags=["Brands"])
def get_all_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return {"brands": read_all_brands(db, skip=skip, limit=limit)}


@app.patch("/brands/{brand_id}", response_model=ListOfBrands, tags=["Brands"])
def patch_brand(
    data: BrandsBaseOptionalBody,
    brand_id: UUID = Path(title="The id of the brand to update"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user.id
    for key, value in update_data.items():
        if key == "category_id":
            category = read_category(db, param={"id": value})
            if category is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category must exist")
        setattr(brand, key, value)
    return {"brands": [update_brand(db, brand)]}


@app.delete("/brands/{brand_id}", response_model=ListOfBrands, tags=["Brands"])
def delete_brand(
    brand_id: UUID = Path(title="The id of the brand to delete"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    brand = read_brand(db, param={"id": brand_id})
    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by": current_user.id}
    for key, value in deleted_dict.items():
        setattr(brand, key, value)
    return {"brands": [update_brand(db, brand)]}


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
    category_name = read_category(db, param={"name": data.name})
    if category_name is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category with this name already exists")
    return create_category(db, data, current_user.id)


@app.get(
    "/categories",
    response_model=List[CategoriesResponse],
    dependencies=[Depends(get_current_user)],
    tags=["Categories"],
)
def get_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return read_all_categories(db, skip=skip, limit=limit)


@app.patch(
    "/categories/{category_id}",
    response_model=CategoriesResponse,
    tags=["Categories"],
)
def patch_category(
    data: CategoriesBaseOptionalBody,
    category_id: UUID = Path(title="The id of the category to update"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    update_data = data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    update_data["updated_by"] = current_user.id
    for key, value in update_data.items():
        setattr(category, key, value)
    return update_category(db, category)


@app.delete("/categories/{category_id}", tags=["Categories"])
def delete_category(
    category_id: UUID = Path(title="The id of the category to delete"),
    db: Session = Depends(get_db),
    current_user: SystemUser = Depends(get_current_user),
):
    category = read_category(db, param={"id": category_id})
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    deleted_dict = {"deleted_at": datetime.now(), "deleted_by": current_user.id}
    for key, value in deleted_dict.items():
        setattr(category, key, value)
    return update_category(db, category)


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
