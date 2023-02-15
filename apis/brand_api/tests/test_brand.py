from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from ..db.models import Brands, Categories
from ..main import app
from .conftest import validate_timestamp_and_ownership

client = TestClient(app)

methods = [client.patch, client.delete]
methods_brand_id = [client.post, client.get]

# DEFAULT BEHAVIOUR
@pytest.mark.unit
def test_success_brand_creation(db_session, token_generator, create_valid_category):
    category_id = db_session.query(Categories).first().id
    response = client.post(
        "/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validBrandName",
            "website": "www.validsite.pt",
            "category_id": str(category_id),
            "description": "Desc",
            "average_price": "10€",
            "rating": 5,
        },
    )
    assert response.status_code == 201
    assert len(response.json()["brands"]) >= 1
    validate_timestamp_and_ownership(response.json()["brands"], "post")


@pytest.mark.unit
def test_success_brands_read(token_generator, create_valid_brand):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["brands"]) >= 1
    validate_timestamp_and_ownership(response.json()["brands"], "get")


@pytest.mark.unit
def test_success_brands_read_non_deleted(token_generator, delete_brand):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["brands"]) == 0


@pytest.mark.unit
def test_success_brand_update_name(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brands).first().id
    response = client.patch(
        f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator}, json={"name": "updatedBrandName"}
    )
    assert response.status_code == 200
    for res in response.json()["brands"]:
        assert res["name"] == "updatedBrandName"
    validate_timestamp_and_ownership(response.json()["brands"], "patch")


@pytest.mark.unit
def test_success_brand_update_category(db_session, token_generator, create_valid_brand):
    update_category = Categories(name="updateCategoryName", description="updateDescriptionName", price_per_category=1)
    db_session.add(update_category)
    db_session.commit()
    db_session.refresh(update_category)

    brand_id = db_session.query(Brands).first().id
    response = client.patch(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"category_id": str(update_category.id)},
    )
    assert response.status_code == 200
    for res in response.json()["brands"]:
        assert res["category_id"] == str(update_category.id)
    validate_timestamp_and_ownership(response.json()["brands"], "patch")


@pytest.mark.unit
def test_success_brand_delete(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brands).first().id
    response = client.delete(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    validate_timestamp_and_ownership(response.json()["brands"], "delete")
    brands_list = db_session.query(Brands).all()
    assert len(brands_list) > 0


# ERROR HANDLING
@pytest.mark.unit
def test_error_method_brand_not_allowed():
    for met in methods:
        response = met("/brands")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_method_brand_id_not_allowed():
    for met in methods_brand_id:
        response = met(f"/brands/{uuid4()}")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_get_brand_not_authorized():
    response = client.get("/brands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_delete_brand_id_not_authorized():
    response = client.delete(f"/brands/{uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_delete_brand_does_not_exist(token_generator, create_valid_brand):
    response = client.delete(f"/brands/{uuid4()}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Brand not found"


@pytest.mark.unit
def test_error_update_brand_category_must_exist(db_session, token_generator, create_valid_brand):
    random_category_id = uuid4()
    brand_id = db_session.query(Brands).first().id
    response = client.patch(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"category_id": str(random_category_id)},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category must exist"


@pytest.mark.unit
def test_error_brands_delete_deleted_brand(db_session, token_generator, delete_brand):
    brand_id = db_session.query(Brands).first().id
    response = client.delete(
        f"/brands/{brand_id}",
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Brand not found"


@pytest.mark.unit
def test_error_create_brand_category_must_exist(db_session, token_generator, create_valid_brand):
    random_category_id = uuid4()
    response = client.post(
        f"/brands",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "validBrandName",
            "website": "www.validsite.pt",
            "category_id": str(random_category_id),
            "description": "Desc",
            "average_price": "10€",
            "rating": 5,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category must exist"
