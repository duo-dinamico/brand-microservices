from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from .. import schemas
from ..db.models import Brand, Category
from ..main import app
from .conftest import validate_ownership_keys, validate_timestamp_and_ownership

client = TestClient(app)

methods = [client.patch, client.delete]
methods_brand_id = [client.post]


# DEFAULT BEHAVIOUR
@pytest.mark.brand
def test_success_brand_creation(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Category).first().id
    response = client.post(
        "/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validBrandName",
            "category_id": str(category_id),
            "description": "Desc",
            "average_price": "medium",
        },
    )
    assert response.status_code == 201
    assert len(response.json()["brands"]) >= 1
    validate_ownership_keys(response.json(), "brands", schemas.BrandsResponse)
    validate_timestamp_and_ownership(response.json()["brands"], "post")


@pytest.mark.brand
def test_success_brands_read(token_generator, create_valid_brand):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["brands"]) >= 1
    validate_ownership_keys(response.json(), "brands", schemas.BrandsResponse)
    validate_timestamp_and_ownership(response.json()["brands"], "get")


@pytest.mark.brand
def test_success_brands_read_orderby_name(token_generator, create_multiple_brands):
    response = client.get(
        "/brands", params={"order_by": "name"}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 200
    name_list = [user["name"] for user in response.json()["brands"]]
    assert sorted(name_list) == name_list


@pytest.mark.brand
def test_success_brands_read_orderby_name_desc(token_generator, create_multiple_brands):
    response = client.get(
        "/brands",
        params={"order_by": "name", "direction": "desc"},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    name_list = [user["name"] for user in response.json()["brands"]]
    assert sorted(name_list, reverse=True) == name_list


@pytest.mark.brand
def test_success_brands_read_query_category_id(db_session, token_generator, create_multiple_brands):
    category_id = db_session.query(Category).offset(1).first().id
    response = client.get(
        "/brands",
        params={"category_id": category_id},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    assert len(response.json()["brands"]) == 2
    for res in response.json()["brands"]:
        assert res["category"]["id"] == str(category_id)


@pytest.mark.brand
def test_success_brands_read_query_category_id_does_not_exist(token_generator, create_multiple_brands):
    response = client.get(
        "/brands",
        params={"category_id": f"{uuid4()}"},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    assert len(response.json()["brands"]) == 0


@pytest.mark.brand
def test_success_one_brand_read(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.get(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["brands"]) == 1
    validate_ownership_keys(response.json(), "brands", schemas.BrandsResponse)
    validate_timestamp_and_ownership(response.json()["brands"], "get")


@pytest.mark.brand
def test_success_brands_read_non_deleted(token_generator, delete_brand):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["brands"]) == 0


@pytest.mark.brand
def test_success_brand_update_name(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.patch(
        f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator}, json={"name": "updatedBrandName"}
    )
    assert response.status_code == 200
    for res in response.json()["brands"]:
        assert res["name"] == "updatedBrandName"
    validate_ownership_keys(response.json(), "brands", schemas.BrandsResponse)
    validate_timestamp_and_ownership(response.json()["brands"], "patch")


@pytest.mark.brand
def test_success_brand_update_category(db_session, token_generator, create_valid_brand):
    update_target_category = client.post(
        "/categories",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validCategoryName",
        },
    )

    brand_id = db_session.query(Brand).first().id
    response = client.patch(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"category_id": str(update_target_category.json()["categories"][0]["id"])},
    )
    assert response.status_code == 200
    for res in response.json()["brands"]:
        assert res["category"]["id"] == str(update_target_category.json()["categories"][0]["id"])
    validate_timestamp_and_ownership(response.json()["brands"], "patch")


@pytest.mark.brand
def test_success_brand_delete(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.delete(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    validate_ownership_keys(response.json(), "brands", schemas.BrandsResponse)
    validate_timestamp_and_ownership(response.json()["brands"], "delete")
    brands_list = db_session.query(Brand).all()
    assert len(brands_list) > 0


@pytest.mark.brand
def test_success_brands_read_deleted(token_generator, delete_brand):
    response = client.get(
        "/brands", params={"show_deleted": True}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 200
    assert len(response.json()["brands"]) >= 1
    for res in response.json()["brands"]:
        assert res["deleted_at"] != None
        assert res["deleted_by"] != None


@pytest.mark.brand
def test_success_one_brand_read_non_deleted(db_session, token_generator, delete_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.get(
        f"/brands/{brand_id}",
        params={"show_deleted": True},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    assert len(response.json()["brands"]) == 1
    for res in response.json()["brands"]:
        assert res["deleted_at"] != None
        assert res["deleted_by"] != None


# ERROR HANDLING
@pytest.mark.brand
def test_error_method_brand_not_allowed():
    for met in methods:
        response = met("/brands")
        assert response.status_code == 405


@pytest.mark.brand
def test_error_method_brand_id_not_allowed():
    for met in methods_brand_id:
        response = met(f"/brands/{uuid4()}")
        assert response.status_code == 405


@pytest.mark.brand
def test_error_delete_brand_id_not_authorized():
    response = client.delete(f"/brands/{uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.brand
def test_error_delete_brand_does_not_exist(token_generator, create_valid_brand):
    response = client.delete(f"/brands/{uuid4()}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Brand not found"


@pytest.mark.brand
def test_error_update_brand_category_must_exist(db_session, token_generator, create_valid_brand):
    random_category_id = uuid4()
    brand_id = db_session.query(Brand).first().id
    response = client.patch(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"category_id": str(random_category_id)},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category must exist"


@pytest.mark.brand
def test_error_brands_delete_deleted_brand(db_session, token_generator, delete_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.delete(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Brand not found"


@pytest.mark.brand
def test_error_create_brand_category_must_exist(db_session, token_generator, create_valid_brand):
    random_category_id = uuid4()
    response = client.post(
        f"/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validBrandName",
            "category_id": str(random_category_id),
            "description": "Desc",
            "average_price": "medium",
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category must exist"


@pytest.mark.brand
def test_error_one_brand_read_deleted_category(db_session, token_generator, delete_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.get(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Brand not found"


@pytest.mark.brand
def test_error_brand_creation_correct_name_type(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Category).first().id
    response = client.post(
        "/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": 1,
            "category_id": str(category_id),
        },
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: str type expected"


@pytest.mark.brand
def test_error_brand_creation_correct_category_type(token_generator):
    response = client.post(
        "/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "newCategory",
            "category_id": "invalidId",
        },
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "category_id: value is not a valid uuid"


@pytest.mark.brand
def test_error_brand_creation_empty_body(token_generator):
    response = client.post(
        "/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: field required"


@pytest.mark.brand
def test_error_brand_creation_missing_category_id(token_generator):
    response = client.post(
        "/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={"name": "newBrand"},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "category_id: field required"


@pytest.mark.brand
def test_error_brand_update_name_incorrect_type(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.patch(
        f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator}, json={"name": 5}
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: str type expected"


@pytest.mark.brand
def test_error_brand_update_empty_body(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.patch(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator}, json={})
    assert response.status_code == 422
    assert response.json()["message"][0] == "At least one of the keys name or category_id must exist."


@pytest.mark.brand
def test_error_brand_update_category_incorrect_type(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.patch(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"category_id": "invalidUUID"},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "category_id: value is not a valid uuid"


@pytest.mark.brand
def test_error_brands_read_orderby_incorrect(token_generator):
    response = client.get(
        "/brands", params={"order_by": "wrong"}, headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 422
    assert (
        response.json()["message"][0]
        == "order_by: value is not a valid enumeration member; permitted: 'name', 'average_price', 'created_at', 'updated_at'"
    )


@pytest.mark.brand
def test_error_brands_read_direction_incorrect(token_generator):
    response = client.get(
        "/brands",
        params={"order_by": "name", "direction": "incorrect"},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 422
    assert (
        response.json()["message"][0] == "direction: value is not a valid enumeration member; permitted: 'asc', 'desc'"
    )


@pytest.mark.brand
def test_error_brands_read_query_category_id_incorrect_type(token_generator):
    response = client.get(
        "/brands",
        params={"category_id": "incorrecttype"},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "category_id: value is not a valid uuid"
