from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .crud import create_user, read_all_brands, read_all_users, read_user
from .db.database import SessionLocal, engine
from .db.models import Base
from .dependencies import get_current_user
from .schemas import Brands, TokenSchema, UserAuth, UserOut
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


@app.get(
    "/brands",
    response_model=List[Brands],
    dependencies=[Depends(get_current_user)],
)
def get_all_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brands = read_all_brands(db, skip=skip, limit=limit)
    return brands


@app.post("/signup", summary="Create new user", response_model=UserOut, status_code=201)
def post_user(data: UserAuth, db: Session = Depends(get_db)):
    user = read_user(db, email=data.email)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exist")
    user = {"email": data.email, "password": get_hashed_password(data.password)}
    return create_user(db, user)


@app.post("/login", summary="Create access and refresh tokens for user", response_model=TokenSchema)
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
