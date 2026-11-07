from fastapi.testclient import TestClient
from fastapi import status
from main import app

client = TestClient(app)


def test_get_transactions():
    response = client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_transaction():
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 2500,
            "transaction_type": "income",
            "purpose": "Freelance work",
        },
    )

    assert response.status_code == 201
    assert isinstance(response.json(), response.includes(id))
