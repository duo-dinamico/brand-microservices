import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from ..db.database import Base, SessionLocal, engine
from ..db.models import Users
from ..main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_brands():
    response = client.get("/brands")
    assert response.status_code == 200
    assert len(response.json()) >= 0


# ERROR HANDLING
@pytest.mark.integration
def test_error_root():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.integration
def test_error_auth():
    response = client.get("/brands")
    assert response.status_code == 401


@pytest.mark.integration(raises=IntegrityError)
def test_user_exists(db_session):
    db_session.add(Users(email="fakeemail@gmail.com", password="fakepassword"))
    db_session.commit()
    response = client.post("/signup/", json={"email": "fakeemail@gmail.com", "password": "fakepassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exist"
