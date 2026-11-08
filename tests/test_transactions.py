import pytest
from fastapi.testclient import TestClient
from fastapi import status
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_get_transactions(client):
    response = client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_transaction(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 2500,
            "transaction_type": "income",
            "purpose": "Freelance work",
        },
    )

    assert response.status_code == 201

    assert "id" in response.json()
