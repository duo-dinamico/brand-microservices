import pytest
from fastapi.testclient import TestClient

from ..db.models import Categories
from ..main import app

client = TestClient(app)

methods = [client.patch, client.delete]

# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_categories(token_generator, create_valid_category):
    response = client.get("/categories", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.integration
def test_success_categories_creation(db_session, token_generator):
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validCategoryName",
            "description": "Desc",
            "price_per_category": 3,
        },
    )
    assert response.status_code == 201


# ERROR HANDLING
@pytest.mark.integration
def test_error_method_not_allowed():
    for met in methods:
        response = met("/categories")
        assert response.status_code == 405


@pytest.mark.integration
def test_error_not_authorized():
    response = client.get("/categories")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
