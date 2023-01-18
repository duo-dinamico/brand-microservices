import uuid

import pytest
from fastapi.testclient import TestClient

from ..crud import read_brand
from ..db.models import Brands, Categories
from ..main import app

client = TestClient(app)

methods = [client.patch, client.delete]
methods_brand_id = [client.post, client.get, client.patch]

# DEFAULT BEHAVIOUR
@pytest.mark.unit
def test_success_brands(token_generator, create_valid_brand):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 1


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


@pytest.mark.unit
def test_success_brand_delete(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brands).first().id
    response = client.delete(f"/brands/{brand_id}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 204


# ERROR HANDLING
@pytest.mark.unit
def test_error_method_brand_not_allowed():
    for met in methods:
        response = met("/brands")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_method_brand_id_not_allowed():
    for met in methods_brand_id:
        response = met(f"/brands/{uuid.uuid4()}")
        assert response.status_code == 405


@pytest.mark.unit
def test_error_brand_not_authorized():
    response = client.get("/brands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_brand_id_not_authorized():
    response = client.delete(f"/brands/{uuid.uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.unit
def test_error_brand_does_not_exist(token_generator, create_valid_brand):
    response = client.delete(f"/brands/{uuid.uuid4()}", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 404
    assert response.json()["detail"] == "Brand not found"
