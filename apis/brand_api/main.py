import json

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exceptions import HTTPException, RequestValidationError, ValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .crud import create_user, read_user
from .db.database import SessionLocal, engine
from .db.models import Base
from .routers import brands, categories, users
from .schemas import ListOfUsers, ListOfUsersWithEmail, TokenSchema, UserAuth
from .utils.password_hash import get_hashed_password, verify_password
from .utils.tokens import create_access_token, create_refresh_token

Base.metadata.create_all(engine)
db = SessionLocal()

app = FastAPI(
    title="Brands API",
    version="0.1.0",
    description="<h3>An API to manage a data set related to brands that are Made in Portugal.\
        </h3><br /><h2>CAUTION: The data on this API is still in alpha and subject to being \
        deleted without prior notice. Use at your own risk.</h2>",
    redoc_url=None,
)


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
def validation_exception_handler(request, exc):
    # print(f"The client sent invalid data!: {exc}") - Replace by logging
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}

    for error in exc_json:
        error_location = error["loc"][-1]
        if error_location == "__root__":
            response["message"].append(f"{error['msg']}")
        else:
            response["message"].append(error_location + f": {error['msg']}")

    return JSONResponse(response, status_code=422)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def get_db():
    try:
        yield db
    finally:
        db.close()


@app.on_event("shutdown")
def close_db():
    db.close()


app.include_router(brands.router)
app.include_router(categories.router)
app.include_router(users.router)


@app.get("/", status_code=405, include_in_schema=False)
def read_root():
    pass


@app.post("/signup", summary="Create new user", response_model=ListOfUsersWithEmail, status_code=201, tags=["Users"])
def post_user(data: UserAuth, db: Session = Depends(get_db)):
    username_check = read_user(db, param={"username": data.username})
    if username_check is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exist")
    if data.email:
        user_email_check = read_user(db, param={"email": data.email})
        if user_email_check is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exist")
    user = {"username": data.username, "email": data.email, "password": get_hashed_password(data.password)}
    return {"users": [create_user(db, user)]}


@app.post("/login", summary="Create access and refresh tokens for user", response_model=TokenSchema, tags=["Users"])
def post_login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = read_user(db, param={"username": form_data.username})
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    return {
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
    }
