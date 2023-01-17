import uuid

import pytest
from fastapi.testclient import TestClient

from ..db.models import Categories
from ..main import app

client = TestClient(app)

methods = [client.patch, client.delete]
methods_category_id = [client.post, client.get, client.delete]

# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_categories_create(db_session, token_generator):
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


@pytest.mark.integration
def test_success_categories_read(token_generator, create_valid_category):
    response = client.get("/categories", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.integration
def test_success_categories_update_name(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "updatedCategoryName"


@pytest.mark.integration
def test_success_categories_update_description(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"description": "updatedDescription"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "updatedDescription"


@pytest.mark.integration
def test_success_categories_update_price(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"price_per_category": 5},
    )
    assert response.status_code == 200
    assert response.json()["price_per_category"] == 5


# ERROR HANDLING
@pytest.mark.integration
def test_error_method_not_allowed_categories():
    for met in methods:
        response = met("/categories")
        assert response.status_code == 405


@pytest.mark.integration
def test_error_method_not_allowed_categories_id():
    for met in methods_category_id:
        response = met(f"/categories/{uuid.uuid4}")
        assert response.status_code == 405


@pytest.mark.integration
def test_error_not_authorized_categories():
    response = client.get("/categories")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.integration
def test_error_not_authorized_categories_id():
    response = client.patch(f"/categories/{uuid.uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.integration
def test_error_categories_update_nonexistent_category(token_generator, create_valid_category):
    response = client.patch(
        f"/categories/{uuid.uuid4()}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
