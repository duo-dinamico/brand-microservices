import re

import pytest
from fastapi.testclient import TestClient

from ..db.models import Users
from ..main import app
from ..utils.password_hash import get_hashed_password

client = TestClient(app)


# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_brands(db_session):
    db_session.add(Users(email="testemail@gmail.com", password=get_hashed_password("testpassword")))
    db_session.commit()
    token = client.post("/login", data={"username": "testemail@gmail.com", "password": "testpassword"})
    response = client.get("/brands", headers={"Authorization": "Bearer " + token.json()["access_token"]})
    assert response.status_code == 200
    assert len(response.json()) >= 0


@pytest.mark.integration
def test_success_user_creation(db_session):
    response = client.post("/signup", json={"email": "newemail@gmail.com", "password": "newpassword"})
    assert response.status_code == 201
    assert response.json()["email"] == "newemail@gmail.com"
    pattern = "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$"
    assert bool(re.search(pattern, response.json()["id"])) == True


@pytest.mark.integration
def test_success_user_login(db_session):
    db_session.add(Users(email="validemail@gmail.com", password=get_hashed_password("validpassword")))
    db_session.commit()
    response = client.post("/login", data={"username": "validemail@gmail.com", "password": "validpassword"})
    assert response.status_code == 200
    # assert response.json()["detail"] == "User with this email already exist"


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


@pytest.mark.integration
def test_error_user_exists(db_session):
    db_session.add(Users(email="fakeemail@gmail.com", password=get_hashed_password("fakepasswords")))
    db_session.commit()
    response = client.post("/signup/", json={"email": "fakeemail@gmail.com", "password": "fakepassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exist"
