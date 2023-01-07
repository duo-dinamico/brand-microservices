import re

import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_brands(token_generator):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 0


@pytest.mark.integration
def test_success_user_creation(db_session):
    pattern = "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$"
    response = client.post("/signup", json={"email": "newemail@gmail.com", "password": "newpassword"})
    assert response.status_code == 201
    assert response.json()["email"] == "newemail@gmail.com"
    assert bool(re.search(pattern, response.json()["id"])) == True


@pytest.mark.integration
def test_success_user_login(create_valid_user):
    response = client.post("/login", data={"username": "validemail@gmail.com", "password": "validpassword"})
    assert response.status_code == 200


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
def test_error_user_exists(create_valid_user):
    response = client.post("/signup", json={"email": "validemail@gmail.com", "password": "validpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exist"
