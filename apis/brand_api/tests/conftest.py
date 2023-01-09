import pytest
from fastapi.testclient import TestClient

from ..db.database import Base, SessionLocal, engine
from ..db.models import Brands, Categories, Users
from ..main import app
from ..utils.password_hash import get_hashed_password

client = TestClient(app)


@pytest.fixture
def db_session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def create_valid_user(db_session):
    db_session.add(Users(email="validemail@gmail.com", password=get_hashed_password("validpassword")))
    db_session.commit()


@pytest.fixture
def token_generator(create_valid_user):
    return client.post("/login", data={"username": "validemail@gmail.com", "password": "validpassword"}).json()[
        "access_token"
    ]


@pytest.fixture
def create_valid_category(db_session):
    db_session.add(Categories(name="catValidName", description="validCatDesc", price_per_category="two"))
    db_session.commit()


@pytest.fixture
def create_valid_brand(db_session, create_valid_category):
    category_id = db_session.query(Categories).first().id
    db_session.add(
        Brands(
            name="validBrandName",
            website="www.validsite.pt",
            category_id=category_id,
            description="Desc",
            average_price="10€",
            rating=5,
        )
    )
    db_session.commit()
