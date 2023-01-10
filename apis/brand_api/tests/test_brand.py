import re

import pytest
from fastapi.testclient import TestClient

from ..db.models import Categories
from ..main import app

client = TestClient(app)

methods = [client.patch, client.delete]

# DEFAULT BEHAVIOUR
@pytest.mark.integration
def test_success_brands(token_generator, create_valid_brand):
    response = client.get("/brands", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.integration
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


# ERROR HANDLING
@pytest.mark.integration
def test_error_method_not_allowed():
    for met in methods:
        response = met("/brands")
        assert response.status_code == 405


@pytest.mark.integration
def test_error_not_authorized():
    response = client.get("/brands")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
