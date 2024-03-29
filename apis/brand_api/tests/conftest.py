from re import search

import pytest
from fastapi.testclient import TestClient

from ..db.database import SessionLocal, engine
from ..db.models import Base, Brand, BrandSocial, Category, Role, Social, User
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
def create_valid_role(db_session):
    db_session.add(Role(name="admin"))
    db_session.commit()


@pytest.fixture
def create_valid_social(db_session):
    db_session.add(Social(name="Website"))
    db_session.commit()


@pytest.fixture
def create_valid_user(db_session):
    db_session.add(User(username="validUser", password=get_hashed_password("ValidPassword1")))
    db_session.commit()


@pytest.fixture
def create_multiple_users(db_session):
    db_session.add(User(username="validUser2", password=get_hashed_password("ValidPassword2")))
    db_session.add(User(username="validUser1", password=get_hashed_password("ValidPassword1")))
    db_session.add(User(username="validUser3", password=get_hashed_password("ValidPassword3")))
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
    db_session.add(Category(name="catValidName", created_by_id=user_id))
    db_session.commit()


@pytest.fixture
def create_multiple_categories(db_session, create_valid_user):
    user_id = db_session.query(User).first().id
    db_session.add(Category(name="catValidName3", created_by_id=user_id))
    db_session.add(Category(name="catValidName4", created_by_id=user_id))
    db_session.add(Category(name="catValidName1", created_by_id=user_id))
    db_session.commit()


@pytest.fixture
def create_valid_brand(db_session, create_valid_category):
    category_id = db_session.query(Category).first().id
    user_id = db_session.query(User).first().id
    db_session.add(
        Brand(
            name="validBrandName",
            category_id=category_id,
            description="Desc",
            average_price="medium",
            created_by_id=user_id,
        )
    )
    db_session.commit()


@pytest.fixture
def create_multiple_brands(db_session, create_multiple_categories):
    category_id_1 = db_session.query(Category).first().id
    category_id_2 = db_session.query(Category).offset(1).first().id
    user_id = db_session.query(User).first().id
    db_session.add(
        Brand(
            name="validBrandName3",
            category_id=category_id_1,
            description="Desc",
            average_price="medium",
            created_by_id=user_id,
        )
    )
    db_session.add(
        Brand(
            name="validBrandName2",
            category_id=category_id_2,
            description="Desc",
            average_price="medium",
            created_by_id=user_id,
        )
    )
    db_session.add(
        Brand(
            name="validBrandName5",
            category_id=category_id_2,
            description="Desc",
            average_price="medium",
            created_by_id=user_id,
        )
    )
    db_session.commit()


@pytest.fixture
def create_valid_brand_social(db_session, create_valid_brand, create_valid_social):
    brand_id = db_session.query(Brand).first().id
    social_id = db_session.query(Social).first().id
    user_id = db_session.query(User).first().id
    db_session.add(
        BrandSocial(brand_id=brand_id, social_id=social_id, address="www.website.com", created_by_id=user_id)
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


@pytest.fixture
def delete_brand_social(db_session, create_valid_brand_social, token_generator):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    return client.delete(
        f"/brands/{brand_id}/socials/{brand_socials_id}", headers={"Authorization": "Bearer " + token_generator}
    )


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
