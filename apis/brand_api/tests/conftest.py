import pytest
from fastapi.testclient import TestClient

from ..db.database import Base, SessionLocal, engine
from ..db.models import Users
from ..main import app
from ..utils.password_hash import get_hashed_password

client = TestClient(app)


@pytest.fixture
def db_session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    Base.metadata.drop_all(engine)
    session.close()


@pytest.fixture
def create_valid_user(db_session):
    db_session.add(Users(email="validemail@gmail.com", password=get_hashed_password("validpassword")))
    db_session.commit()


@pytest.fixture
def token_generator(create_valid_user):
    return client.post("/login", data={"username": "validemail@gmail.com", "password": "validpassword"}).json()[
        "access_token"
    ]
