from re import search
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from .. import schemas
from ..db.models import Category
from ..main import app
from .conftest import validate_ownership_keys, validate_timestamp_and_ownership

client = TestClient(app)

methods = [client.patch, client.put, client.delete]
methods_category_id = [client.post]


# DEFAULT BEHAVIOUR
@pytest.mark.categories
def test_success_categories_create(token_generator):
    pattern = "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$"
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validCategoryName",
        },
    )
    assert response.status_code == 201
    assert len(response.json()["categories"]) >= 1
    for res in response.json()["categories"]:
        assert res["name"] == "validCategoryName"
        assert bool(search(pattern, res["id"])) == True
    validate_ownership_keys(response.json(), "categories", schemas.CategoriesResponse)
    validate_timestamp_and_ownership(response.json()["categories"], "post")


@pytest.mark.categories
def test_success_categories_read(token_generator, create_valid_category):
    response = client.get("/categories", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["categories"]) >= 1
    validate_ownership_keys(response.json(), "categories", schemas.CategoriesResponse)
    validate_timestamp_and_ownership(response.json()["categories"], "get")


@pytest.mark.categories
def test_success_categories_read_orderby_name(token_generator, create_multiple_categories):
    response = client.get(
        "/categories", params={"order_by": "name"}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 200
    name_list = [user["name"] for user in response.json()["categories"]]
    assert sorted(name_list) == name_list


@pytest.mark.categories
def test_success_categories_read_orderby_name_desc(token_generator, create_multiple_categories):
    response = client.get(
        "/categories",
        params={"order_by": "name", "direction": "desc"},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    name_list = [user["name"] for user in response.json()["categories"]]
    assert sorted(name_list, reverse=True) == name_list


@pytest.mark.categories
def test_success_one_category_read(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Category).first().id
    response = client.get(f"/categories/{category_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["categories"]) == 1
    for res in response.json()["categories"]:
        assert res["name"] == "catValidName"
        assert res["id"] == str(category_id)
    validate_ownership_keys(response.json(), "categories", schemas.CategoriesResponse)
    validate_timestamp_and_ownership(response.json()["categories"], "get")


@pytest.mark.categories
def test_success_categories_read_non_deleted(token_generator, delete_category):
    response = client.get("/categories", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["categories"]) == 0


@pytest.mark.categories
def test_success_categories_update_name(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Category).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 200
    for res in response.json()["categories"]:
        assert res["name"] == "updatedCategoryName"
    validate_ownership_keys(response.json(), "categories", schemas.CategoriesResponse)
    validate_timestamp_and_ownership(response.json()["categories"], "patch")


@pytest.mark.categories
def test_success_categories_delete(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Category).first().id
    response = client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    validate_ownership_keys(response.json(), "categories", schemas.CategoriesResponse)
    validate_timestamp_and_ownership(response.json()["categories"], "delete")
    categories_list = db_session.query(Category).all()
    assert len(categories_list) > 0


@pytest.mark.categories
def test_success_categories_read_deleted(token_generator, delete_category):
    response = client.get(
        "/categories", params={"show_deleted": True}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 200
    assert len(response.json()["categories"]) >= 1
    for res in response.json()["categories"]:
        assert res["deleted_at"] != None
        assert res["deleted_by"] != None


@pytest.mark.categories
def test_success_one_category_read_non_deleted(db_session, token_generator, delete_category):
    category_id = db_session.query(Category).first().id
    response = client.get(
        f"/categories/{category_id}",
        params={"show_deleted": True},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    assert len(response.json()["categories"]) == 1
    for res in response.json()["categories"]:
        assert res["deleted_at"] != None
        assert res["deleted_by"] != None


# ERROR HANDLING
@pytest.mark.categories
def test_error_method_not_allowed_categories():
    for met in methods:
        response = met("/categories")
        assert response.status_code == 405


@pytest.mark.categories
def test_error_method_not_allowed_categories_id():
    for met in methods_category_id:
        response = met(f"/categories/{uuid4()}")
        assert response.status_code == 405


@pytest.mark.categories
def test_error_not_authorized_categories():
    response = client.post("/categories")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.categories
def test_error_categories_update_nonexistent_category(token_generator, create_valid_category):
    response = client.patch(
        f"/categories/{uuid4()}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.categories
def test_error_categories_delete_nonexistent_category(token_generator):
    response = client.delete(f"/categories/{uuid4()}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.categories
def test_error_categories_post_existing_category_name(token_generator, create_valid_category):
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "catValidName"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Category with this name already exists"


@pytest.mark.categories
def test_error_categories_patch_deleted_category(db_session, token_generator, delete_category):
    category_id = db_session.query(Category).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "updatedCategoryName"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.categories
def test_error_categories_delete_deleted_category(db_session, token_generator, delete_category):
    category_id = db_session.query(Category).first().id
    response = client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.categories
def test_error_one_category_read_deleted_category(db_session, token_generator, delete_category):
    category_id = db_session.query(Category).first().id
    response = client.get(f"/categories/{category_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.categories
def test_error_categories_create_incorrect_type_name(token_generator):
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": 1,
            "description": "Desc",
            "price_per_category": 3,
        },
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: str type expected"


@pytest.mark.categories
def test_error_categories_create_additional_keys_not_allowed(token_generator):
    response = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validName",
            "not_allowed_key": "should not be here",
        },
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "not_allowed_key: extra fields not permitted"


@pytest.mark.categories
def test_error_categories_update_empty_body(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Category).first().id
    response = client.patch(
        f"/categories/{category_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: field required"


@pytest.mark.categories
def test_error_categories_read_orderby_incorrect(token_generator):
    response = client.get(
        "/categories", params={"order_by": "wrong"}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 422
    assert (
        response.json()["message"][0]
        == "order_by: value is not a valid enumeration member; permitted: 'name', 'created_at', 'updated_at'"
    )


@pytest.mark.categories
def test_error_categories_read_direction_incorrect(token_generator):
    response = client.get(
        "/categories", params={"direction": "sideways"}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 422
    assert (
        response.json()["message"][0] == "direction: value is not a valid enumeration member; permitted: 'asc', 'desc'"
    )
