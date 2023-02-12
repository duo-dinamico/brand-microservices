import uuid

import pytest
from fastapi.testclient import TestClient

from ..db.models import Categories
from ..main import app
from .conftest import validate_timestamp_and_ownership

client = TestClient(app)

methods = [client.patch, client.delete]
methods_category_id = [client.post, client.get]

# DEFAULT BEHAVIOUR
@pytest.mark.unit
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
    assert len(response.json()["categories"]) >= 1
    validate_timestamp_and_ownership(response.json()["categories"], "post")


@pytest.mark.unit
def test_success_categories_read(token_generator, create_valid_category):
    response = client.get("/categories", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["categories"]) >= 1
    validate_timestamp_and_ownership(response.json()["categories"], "get")


@pytest.mark.unit
def test_success_categories_read_non_deleted(token_generator, delete_category):
    response = client.get("/categories", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["categories"]) == 0


@pytest.mark.unit
def test_success_categories_update_name(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 200
    for res in response.json()["categories"]:
        assert res["name"] == "updatedCategoryName"
    validate_timestamp_and_ownership(response.json()["categories"], "patch")


@pytest.mark.unit
def test_success_categories_update_description(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"description": "updatedDescription"},
    )
    assert response.status_code == 200
    for res in response.json()["categories"]:
        assert res["description"] == "updatedDescription"
    validate_timestamp_and_ownership(response.json()["categories"], "patch")


@pytest.mark.unit
def test_success_categories_update_price(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"price_per_category": 5},
    )
    assert response.status_code == 200
    for res in response.json()["categories"]:
        assert res["price_per_category"] == 5
    validate_timestamp_and_ownership(response.json()["categories"], "patch")


@pytest.mark.unit
def test_success_categories_delete(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    validate_timestamp_and_ownership(response.json()["categories"], "delete")
    categories_list = db_session.query(Categories).all()
    assert len(categories_list) > 0


# ERROR HANDLING
@pytest.mark.unit
def test_error_method_not_allowed_categories():
    for met in methods:
        response = met("/categories")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_method_not_allowed_categories_id():
    for met in methods_category_id:
        response = met(f"/categories/{uuid.uuid4}")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_not_authorized_post_categories():
    response = client.post("/categories")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_not_authorized_get_categories():
    response = client.get("/categories")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_not_authorized_patch_categories_id():
    response = client.patch(f"/categories/{uuid.uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_not_authorized_delete_categories_id():
    response = client.delete(f"/categories/{uuid.uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_categories_update_nonexistent_category(token_generator, create_valid_category):
    response = client.patch(
        f"/categories/{uuid.uuid4()}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.unit
def test_error_categories_update_wrong_price(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"price_per_category": 8},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "value is not a valid enumeration member; permitted: 1, 2, 3, 4, 5"


@pytest.mark.unit
def test_error_categories_delete_nonexistent_category(token_generator):
    response = client.delete(f"/categories/{uuid.uuid4()}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.unit
def test_error_categories_post_existing_category_name(token_generator, create_valid_category):
    response = client.post(
        "/categories", headers={"Authorization": "Bearer " + token_generator}, json={"name": "catValidName"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Category with this name already exists"


@pytest.mark.unit
def test_error_categories_patch_deleted_category(db_session, token_generator, delete_category):
    category_id = db_session.query(Categories).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.unit
def test_error_categories_delete_deleted_category(db_session, token_generator, delete_category):
    category_id = db_session.query(Categories).first().id
    response = client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
