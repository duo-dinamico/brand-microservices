import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


@pytest.mark.integration
def test_error_root():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.integration
def test_success_users():
    response = client.get("/users")
    assert response.status_code == 200
    print(response.json)
