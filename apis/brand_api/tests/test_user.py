import re

import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)

methods_auth = [client.get, client.patch, client.delete]
methods_users = [client.post, client.patch, client.delete]

# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_users(create_valid_user, token_generator):
    response = client.get("/users", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 1


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
def test_error_method_not_allowed_users():
    for met in methods_users:
        response = met("/users")
        assert response.status_code == 405


@pytest.mark.integration
def test_error_method_not_allowed_auth():
    for met in methods_auth:
        response_signup = met("/signup")
        assert response_signup.status_code == 405
        response_login = met("/login")
        assert response_login.status_code == 405


@pytest.mark.integration
def test_error_user_exists(create_valid_user):
    response = client.post("/signup", json={"email": "validemail@gmail.com", "password": "validpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exist"
