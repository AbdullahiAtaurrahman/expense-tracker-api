import pytest
import asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import delete, select

from main import app

from app.database import create_test_engine, get_db
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.recurring_transaction import RecurringTransaction
from app.models.user import User
from app.core.security import hash_password, create_access_token

test_engine = create_test_engine()

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


async def clear_test_database():
    async with TestingSessionLocal() as session:
        await session.execute(delete(Transaction))
        await session.execute(delete(Budget))
        await session.execute(delete(RecurringTransaction))
        await session.execute(delete(User))
        await session.commit()


async def create_test_user(email="test@example.com"):
    async with TestingSessionLocal() as session:
        user = User(
            email=email,
            hashed_password=hash_password("testpassword123"),
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user.id


@pytest.fixture(autouse=True)
def clean_database():
    asyncio.run(clear_test_database())

    yield

    asyncio.run(clear_test_database())


@pytest.fixture
def auth_headers(clean_database):

    user_id = asyncio.run(create_test_user())

    token = create_access_token(data={"sub": str(user_id)})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_auth_headers(clean_database):
    user_id = asyncio.run(create_test_user("second@example.com"))

    token = create_access_token(data={"sub": str(user_id)})

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(auth_headers):
    with TestClient(app, headers=auth_headers) as test_client:
        yield test_client


@pytest.fixture
def second_client(second_auth_headers):
    with TestClient(app, headers=second_auth_headers) as test_client:
        yield test_client


@pytest.fixture
def deactivate_default_test_user():
    def deactivate():
        async def deactivate_user():
            async with TestingSessionLocal() as session:
                user = await session.scalar(
                    select(User).where(User.email == "test@example.com")
                )

                assert user is not None

                user.is_active = False
                await session.commit()

        asyncio.run(deactivate_user())

    return deactivate


@pytest.fixture
def get_user_by_email():
    def get_user(email):
        async def fetch_user():
            async with TestingSessionLocal() as session:
                return await session.scalar(select(User).where(User.email == email))

        return asyncio.run(fetch_user())

    return get_user
