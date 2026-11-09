import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import status
from main import app

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import delete

from app.models.transaction import Transaction
from app.database import create_test_engine, get_db

test_engine = create_test_engine()

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_database():
    # Clean before the test
    asyncio.run(clear_test_database())

    yield

    # Clean after the test
    asyncio.run(clear_test_database())


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


async def clear_test_database():
    async with TestingSessionLocal() as session:
        await session.execute(delete(Transaction))
        await session.commit()


def test_get_transactions(client):
    response = client.get("/api/v1/transactions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_transaction_by_id(client):

    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 200
    assert create_response.json()["id"] == transaction_id
    assert create_response.json()["transaction_type"] == "income"
    assert create_response.json()["purpose"] == "Freelance project"


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


def test_create_transaction_with_negative_amount(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": -500,
            "transaction_type": "expense",
            "purpose": "Invalid transaction",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_invalid_type(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "savings",
            "purpose": "Invalid transaction type",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_long_purpose(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "purpose": "A" * 201,
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_empty_purpose(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
            "purpose": "",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_zero_amount(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 0,
            "transaction_type": "expense",
            "purpose": "Zero amount",
        },
    )

    assert response.status_code == 422


def test_create_transaction_with_missing_field(client):
    response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 500,
            "transaction_type": "expense",
        },
    )

    assert response.status_code == 422


def test_update_transaction(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={
            "amount": 2000,
            "purpose": "Completed freelance project",
        },
    )

    assert response.status_code == 200
    assert response.json()["amount"] == 2000
    assert response.json()["purpose"] == "Completed freelance project"
    assert response.json()["transaction_type"] == "income"


def test_update_nonexistent_transaction(client):

    response = client.patch(
        "/api/v1/transactions/999999",
        json={
            "amount": 2000,
        },
    )

    assert response.status_code == 404


def test_update_transaction_with_invalid_amount(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"amount": -200},
    )

    assert response.status_code == 422


def test_update_transaction_with_empty_purpose(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"purpose": ""},
    )

    assert response.status_code == 422


def test_update_transaction_with_invalid_type(client):
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "income",
            "purpose": "Freelance project",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"transaction_type": "savings"},
    )

    assert response.status_code == 422


def test_delete_transaction(client):

    create_response = client.post(
        "/api/v1/transactions",
        json={
            "amount": 1500,
            "transaction_type": "expense",
            "purpose": "Internet subscription",
        },
    )

    transaction_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/transactions/{transaction_id}")

    assert response.status_code == 204

    get_response = client.get(f"/api/v1/transactions/{transaction_id}")

    assert get_response.status_code == 404


def test_nonexistent_transaction(client):

    response = client.get("/api/v1/transactions/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction with ID 99999 not found"
