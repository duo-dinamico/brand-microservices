import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)

# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_brands():
    response = client.get("/brands")
    assert response.status_code == 200
    assert len(response.json()) >= 0


@pytest.mark.integration
def test_success_signup():
    new_user = {"email": "fakeeeeeeeeeeeeemail@gmail.com", "password": "fakepassword"}
    response = client.post("/signup/", json=new_user)
    assert response.json()["email"] == new_user["email"]
    assert response.status_code == 201


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
