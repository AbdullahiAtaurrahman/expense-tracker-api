from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_transactions():
    response = client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
