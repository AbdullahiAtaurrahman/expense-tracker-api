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
