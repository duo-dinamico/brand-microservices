from re import search

import pytest
from fastapi.testclient import TestClient

from .. import schemas
from ..main import app
from .conftest import validate_ownership_keys, validate_timestamp_and_ownership

client = TestClient(app)

methods = [client.patch, client.delete]


# DEFAULT BEHAVIOUR
@pytest.mark.socials
def test_success_socials_create(token_generator):
    pattern = "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$"
    response = client.post(
        "/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "website",
        },
    )
    assert response.status_code == 201
    assert len(response.json()["socials"]) >= 1
    for res in response.json()["socials"]:
        assert res["name"] == "website"
        assert bool(search(pattern, res["id"])) == True
    validate_ownership_keys(response.json(), "socials", schemas.SocialsBase)
    validate_timestamp_and_ownership(response.json()["socials"], "post")


@pytest.mark.socials
def test_success_socials_read(token_generator, create_valid_social):
    response = client.get("/socials", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["socials"]) >= 1
    validate_ownership_keys(response.json(), "socials", schemas.SocialsBase)
    validate_timestamp_and_ownership(response.json()["socials"], "get")


# ERROR HANDLING
@pytest.mark.socials
def test_error_method_not_allowed():
    for met in methods:
        response = met("/socials")
        assert response.status_code == 405


@pytest.mark.socials
def test_error_social_creation_correct_name_type(token_generator, create_valid_social):
    response = client.post(
        "/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": 1,
        },
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: str type expected"


@pytest.mark.socials
def test_error_social_creation_empty_body(token_generator):
    response = client.post(
        "/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "name: field required"
