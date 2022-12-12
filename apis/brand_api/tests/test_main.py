from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_error_root():
    response = client.get("/")
    assert response.status_code == 400
    assert response.json() == {"msg": "Bad Request"}