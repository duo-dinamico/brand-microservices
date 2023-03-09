from re import search

import pytest
from fastapi.testclient import TestClient

from ..db.database import SessionLocal, engine
from ..db.models import Base, Brand, Category, User
from ..main import app
from ..utils.password_hash import get_hashed_password

client = TestClient(app)


@pytest.fixture
def db_session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def create_valid_user(db_session):
    db_session.add(User(username="validUser", password=get_hashed_password("ValidPassword1")))
    db_session.commit()


@pytest.fixture
def create_valid_user_with_email(db_session):
    db_session.add(
        User(
            username="validUserWithEmail",
            email="validemail@duodinamico.online",
            password=get_hashed_password("ValidPassword1"),
        )
    )
    db_session.commit()


@pytest.fixture
def token_generator(create_valid_user):
    return client.post("/login", data={"username": "validUser", "password": "ValidPassword1"}).json()["access_token"]


@pytest.fixture
def create_valid_category(db_session, create_valid_user):
    user_id = db_session.query(User).first().id
    db_session.add(
        Category(name="catValidName", description="validCatDesc", price_per_category="two", created_by_id=user_id)
    )
    db_session.commit()


@pytest.fixture
def create_valid_brand(db_session, create_valid_category):
    category_id = db_session.query(Category).first().id
    user_id = db_session.query(User).first().id
    db_session.add(
        Brand(
            name="validBrandName",
            website="www.validsite.pt",
            category_id=category_id,
            description="Desc",
            average_price="10€",
            rating=5,
            created_by_id=user_id,
        )
    )
    db_session.commit()


@pytest.fixture
def delete_category(db_session, create_valid_category, token_generator):
    category_id = db_session.query(Category).first().id
    return client.delete(f"/categories/{category_id}", headers={"Authorization": "Bearer " + token_generator})


@pytest.fixture
def delete_brand(db_session, create_valid_brand, token_generator):
    brand_id = db_session.query(Brand).first().id
    return client.delete(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator})


@pytest.fixture
def delete_user(db_session, create_valid_user, token_generator):
    user_id = db_session.query(User).first().id
    return client.delete(f"/users/{user_id}", headers={"Authorization": "Bearer " + token_generator})


# TODO: Validation should probably become a class with these two as methods inside to check everything in one go
def validate_timestamp(data, method):
    pattern = "^[0-9]{4}-[0-1]{1}[0-9]{1}-[0-3]{1}[0-9]{1}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{6}$"
    for key, value in data.items():
        if key == "created_at":
            assert value != None
        if key == "updated_at":
            if method == "post" or method == "get" or method == "delete":
                assert value == None
            else:
                assert bool(search(pattern, value)) == True
                assert value != None
        if key == "deleted_at":
            if method == "post" or method == "get" or method == "patch":
                assert value == None
            else:
                assert bool(search(pattern, value)) == True
                assert value != None


def validate_ownership(data, method):
    for key, value in data.items():
        if key == "created_by":
            assert value != None
        if key == "updated_by":
            if method == "post" or method == "get" or method == "delete":
                assert value == None
            else:
                assert value != None
        if key == "deleted_by":
            if method == "post" or method == "get" or method == "patch":
                assert value == None
            else:
                assert value != None


def validate_timestamp_and_ownership(data, method):
    for res in data:
        validate_timestamp(res, method)
        validate_ownership(res, method)


def validate_ownership_keys(data, field, schema):
    for res in data[field]:
        for key, value in res.items():
            assert key in schema.__fields__
            if key == "created_by":
                assert type(value) is dict
            if key == "updated_by":
                assert type(value) is dict or type(value) == str or value == None
            if key == "deleted_by":
                assert type(value) is dict or type(value) == str or value == None
