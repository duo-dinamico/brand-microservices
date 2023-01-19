import re
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from ..db.models import Users
from ..main import app

client = TestClient(app)

methods_auth = [client.get, client.patch]
methods_users = [client.post, client.patch]

# DEFAULT BEHAVIOUR
@pytest.mark.unit
def test_success_users(create_valid_user, token_generator):
    response = client.get("/users", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.unit
def test_success_user_creation(db_session):
    pattern = "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$"
    response = client.post("/signup", json={"email": "newemail@gmail.com", "password": "newpassword"})
    assert response.status_code == 201
    assert response.json()["email"] == "newemail@gmail.com"
    assert bool(re.search(pattern, response.json()["id"])) == True


@pytest.mark.unit
def test_success_user_login(create_valid_user):
    response = client.post("/login", data={"username": "validemail@gmail.com", "password": "validpassword"})
    assert response.status_code == 200


@pytest.mark.unit
def test_success_user_delete(db_session, token_generator, create_valid_user) -> None:
    user_id = db_session.query(Users).first().id
    response = client.delete(f"/users/{user_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 204
    user_deleted = db_session.query(Users).all()
    assert user_deleted == []


# ERROR HANDLING
@pytest.mark.unit
def test_error_method_not_allowed_users():
    for met in methods_users:
        response = met("/users")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_method_not_allowed_auth():
    for met in methods_auth:
        response_signup = met("/signup")
        assert response_signup.status_code == 405
        response_login = met("/login")
        assert response_login.status_code == 405


@pytest.mark.unit
def test_error_user_delete_non_existing_user(token_generator) -> None:
    response = client.delete(f"/users/{uuid4()}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.unit
def test_error_not_authorized_delete_users_id(db_session, create_valid_user) -> None:
    user_id = db_session.query(Users).first().id
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_user_exists(create_valid_user):
    response = client.post("/signup", json={"email": "validemail@gmail.com", "password": "validpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exist"
