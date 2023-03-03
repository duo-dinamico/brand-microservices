import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)

methods = [client.post, client.get, client.patch, client.delete]

# DEFAULT BEHAVIOUR


# ERROR HANDLING
@pytest.mark.unit
def test_error_method_not_allowed():
    for met in methods:
        response = met("/")
        assert response.status_code == 405
