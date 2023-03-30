from re import search
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from .. import schemas
from ..db.models import Brand, BrandSocial, Social
from ..main import app
from .conftest import validate_ownership_keys, validate_timestamp_and_ownership

client = TestClient(app)

methods = [client.patch, client.delete]
methods_brand_id = [client.get, client.post]
key_checklist = [
    "id",
    "brand",
    "social",
    "address",
    "created_by",
    "created_at",
    "updated_by",
    "updated_at",
    "deleted_by",
    "deleted_at",
]


# DEFAULT BEHAVIOUR
@pytest.mark.brandsocials
def test_success_brand_socials_create(db_session, token_generator, create_valid_brand, create_valid_social):
    brand_id = db_session.query(Brand).first().id
    social_id = db_session.query(Social).first().id
    pattern = "^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$"
    response = client.post(
        f"/brands/{brand_id}/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": str(social_id), "address": "www.brand.com"},
    )
    assert response.status_code == 201
    assert len(response.json()["socials"]) >= 1
    for res in response.json()["socials"]:
        assert res["address"] == "www.brand.com"
        assert res["social"]["name"] == "Website"
        assert bool(search(pattern, res["id"])) == True
        for key in key_checklist:
            assert key in res
    validate_ownership_keys(response.json(), "socials", schemas.BrandSocialsResponse)
    validate_timestamp_and_ownership(response.json()["socials"], "post")


@pytest.mark.brandsocials
def test_success_brand_socials_read(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    response = client.get(f"/brands/{brand_id}/socials", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["socials"]) >= 1
    for res in response.json()["socials"]:
        for key in key_checklist:
            assert key in res
    validate_ownership_keys(response.json(), "socials", schemas.BrandSocialsResponse)
    validate_timestamp_and_ownership(response.json()["socials"], "get")


@pytest.mark.brandsocials
def test_success_brands_socials_read_non_deleted(db_session, token_generator, delete_brand_social):
    brand_id = db_session.query(Brand).first().id
    response = client.get(f"/brands/{brand_id}/socials", headers={"Authorization": "Bearer " + token_generator})
    assert response.status_code == 200
    assert len(response.json()["socials"]) == 0


@pytest.mark.brandsocials
def test_success_brand_socials_update_address(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    response = client.patch(
        f"/brands/{brand_id}/socials/{brand_socials_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"address": "www.newwebsite.com"},
    )
    assert response.status_code == 200
    for res in response.json()["socials"]:
        assert res["address"] == "www.newwebsite.com"
    validate_ownership_keys(response.json(), "socials", schemas.BrandSocialsResponse)
    validate_timestamp_and_ownership(response.json()["socials"], "patch")


@pytest.mark.brandsocials
def test_success_brand_socials_update_social(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    update_target_social = client.post(
        "/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={
            "name": "Mastodon",
        },
    )

    response = client.patch(
        f"/brands/{brand_id}/socials/{brand_socials_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": str(update_target_social.json()["socials"][0]["id"])},
    )
    assert response.status_code == 200
    for res in response.json()["socials"]:
        assert res["social"]["id"] == str(update_target_social.json()["socials"][0]["id"])
    validate_timestamp_and_ownership(response.json()["socials"], "patch")


@pytest.mark.brandsocials
def test_success_brand_socials_delete(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    response = client.delete(
        f"/brands/{brand_id}/socials/{brand_socials_id}", headers={"Authorization": "Bearer " + token_generator}
    )
    assert response.status_code == 200
    validate_ownership_keys(response.json(), "socials", schemas.BrandSocialsResponse)
    validate_timestamp_and_ownership(response.json()["socials"], "delete")
    brand_socials_list = db_session.query(BrandSocial).all()
    assert len(brand_socials_list) > 0


@pytest.mark.brandsocials
def test_success_brands_socials_read_deleted(db_session, token_generator, delete_brand_social):
    brand_id = db_session.query(Brand).first().id
    response = client.get(
        f"/brands/{brand_id}/socials",
        params={"show_deleted": True},
        headers={"Authorization": "Bearer " + token_generator},
    )
    assert response.status_code == 200
    assert len(response.json()["socials"]) >= 1
    for res in response.json()["socials"]:
        assert res["deleted_at"] != None
        assert res["deleted_by"] != None


# ERROR HANDLING
@pytest.mark.brandsocials
def test_error_method_not_allowed(db_session, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    for met in methods:
        response = met(f"/brands/{brand_id}/socials")
        assert response.status_code == 405


@pytest.mark.brandsocials
def test_error_brand_socials_id_method_not_allowed(db_session, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    for met in methods_brand_id:
        response = met(f"/brands/{brand_id}/socials/{brand_socials_id}")
        assert response.status_code == 405


@pytest.mark.brandsocials
def test_error_delete_not_authorized():
    response = client.delete(f"/brands/{uuid4()}/socials/{uuid4()}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.brandsocials
def test_error_create_social_wrong_type(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.post(
        f"/brands/{brand_id}/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": "wrong type", "address": "www.brand.com"},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "social_id: value is not a valid uuid"


@pytest.mark.brandsocials
def test_error_create_address_wrong_type(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.post(
        f"/brands/{brand_id}/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": f"{uuid4()}", "address": 1},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "address: str type expected"


@pytest.mark.brandsocials
def test_error_create_empty_body(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.post(
        f"/brands/{brand_id}/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "social_id: field required"


@pytest.mark.brandsocials
def test_error_create_empty_body(db_session, token_generator, create_valid_brand):
    brand_id = db_session.query(Brand).first().id
    response = client.post(
        f"/brands/{brand_id}/socials",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": f"{uuid4()}"},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "address: field required"


@pytest.mark.brandsocials
def test_error_update_empty_body(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    response = client.patch(
        f"/brands/{brand_id}/socials/{brand_socials_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "At least one of the keys social_id or address must exist."


@pytest.mark.brandsocials
def test_error_update_social_doesnt_exist(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    response = client.patch(
        f"/brands/{brand_id}/socials/{brand_socials_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": f"{uuid4()}"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Social must exist."


@pytest.mark.brandsocials
def test_error_update_address_wrong_type(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    response = client.patch(
        f"/brands/{brand_id}/socials/{brand_socials_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"address": 1},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "address: str type expected"


@pytest.mark.brandsocials
def test_error_update_social_wrong_type(db_session, token_generator, create_valid_brand_social):
    brand_id = db_session.query(Brand).first().id
    brand_socials_id = db_session.query(BrandSocial).first().id
    response = client.patch(
        f"/brands/{brand_id}/socials/{brand_socials_id}",
        headers={"Authorization": "Bearer " + token_generator},
        json={"social_id": "wrong type"},
    )
    assert response.status_code == 422
    assert response.json()["message"][0] == "social_id: value is not a valid uuid"
