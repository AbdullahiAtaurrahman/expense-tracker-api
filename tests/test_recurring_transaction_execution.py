import asyncio
from datetime import date

import pytest

from sqlalchemy import select

from app.models.transaction import Transaction
from app.models.recurring_transaction import RecurringTransaction

from app.repositories.recurring_transaction_execution import (
    RecurringTransactionExecutionRepository,
)

from app.services.recurring_transaction_execution import (
    RecurringTransactionExecutionService,
)

from tests.conftest import TestingSessionLocal, create_test_user


async def create_recurring_transaction(
    frequency="daily",
    start_date=date(2026, 1, 1),
    next_run_date=date(2026, 1, 1),
    end_date=None,
    is_active=True,
):
    user_id = await create_test_user()

    async with TestingSessionLocal() as session:
        recurring = RecurringTransaction(
            user_id=user_id,
            amount=1000,
            transaction_type="expense",
            purpose="Monthly subscription",
            category="Entertainment",
            frequency=frequency,
            start_date=start_date,
            next_run_date=next_run_date,
            end_date=end_date,
            is_active=is_active,
        )

        session.add(recurring)
        await session.commit()
        await session.refresh(recurring)

        return recurring.id, user_id


async def get_transactions():
    async with TestingSessionLocal() as session:
        result = await session.execute(select(Transaction))

        return result.scalars().all()


async def get_recurring_transaction(recurring_id):
    async with TestingSessionLocal() as session:
        return await session.get(
            RecurringTransaction,
            recurring_id,
        )


# -----------------------------------------
# DAILY PROCESSING
# -----------------------------------------


def test_process_daily_recurring_transaction():

    async def run_test():
        recurring_id, user_id = await create_recurring_transaction()

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        transactions = await get_transactions()
        recurring = await get_recurring_transaction(recurring_id)

        assert count == 1
        assert len(transactions) == 1

        assert transactions[0].user_id == user_id
        assert transactions[0].amount == 1000
        assert transactions[0].recurrence_date == date(2026, 1, 1)

        assert recurring.next_run_date == date(2026, 1, 2)

    asyncio.run(run_test())


# -----------------------------------------
# WEEKLY PROCESSING
# -----------------------------------------


def test_process_weekly_recurring_transaction():

    async def run_test():
        recurring_id, _ = await create_recurring_transaction(
            frequency="weekly",
        )

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        recurring = await get_recurring_transaction(recurring_id)

        assert count == 1
        assert recurring.next_run_date == date(2026, 1, 8)

    asyncio.run(run_test())


# -----------------------------------------
# MONTHLY PROCESSING
# -----------------------------------------


def test_process_monthly_recurring_transaction():

    async def run_test():
        recurring_id, _ = await create_recurring_transaction(
            frequency="monthly",
        )

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        recurring = await get_recurring_transaction(recurring_id)

        assert count == 1
        assert recurring.next_run_date == date(2026, 2, 1)

    asyncio.run(run_test())


# -----------------------------------------
# YEARLY PROCESSING
# -----------------------------------------


def test_process_yearly_recurring_transaction():

    async def run_test():
        recurring_id, _ = await create_recurring_transaction(
            frequency="yearly",
        )

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        recurring = await get_recurring_transaction(recurring_id)

        assert count == 1
        assert recurring.next_run_date == date(2027, 1, 1)

    asyncio.run(run_test())


# -----------------------------------------
# OVERDUE PROCESSING
# -----------------------------------------


def test_process_all_overdue_occurrences():

    async def run_test():
        recurring_id, _ = await create_recurring_transaction()

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 4))

        transactions = await get_transactions()
        recurring = await get_recurring_transaction(recurring_id)

        assert count == 4
        assert len(transactions) == 4

        assert recurring.next_run_date == date(2026, 1, 5)

    asyncio.run(run_test())


# -----------------------------------------
# DUPLICATE PREVENTION
# -----------------------------------------


def test_prevent_duplicate_recurring_transactions():

    async def run_test():
        recurring_id, user_id = await create_recurring_transaction()

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            await service.process_due_transactions(date(2026, 1, 1))

        # Reset the next run date to simulate
        # an occurrence that has already been generated.

        async with TestingSessionLocal() as session:
            recurring = await session.get(
                RecurringTransaction,
                recurring_id,
            )

            recurring.next_run_date = date(2026, 1, 1)

            await session.commit()

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        transactions = await get_transactions()

        assert count == 0
        assert len(transactions) == 1
        assert transactions[0].user_id == user_id

    asyncio.run(run_test())


# -----------------------------------------
# END DATE PROCESSING
# -----------------------------------------


def test_deactivate_after_end_date():

    async def run_test():
        recurring_id, _ = await create_recurring_transaction(
            end_date=date(2026, 1, 1),
        )

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        transactions = await get_transactions()
        recurring = await get_recurring_transaction(recurring_id)

        assert count == 1
        assert len(transactions) == 1
        assert recurring.is_active is False

    asyncio.run(run_test())


# -----------------------------------------
# INACTIVE RECURRING TRANSACTIONS
# -----------------------------------------


def test_skip_inactive_recurring_transactions():

    async def run_test():
        recurring_id, _ = await create_recurring_transaction(
            is_active=False,
        )

        async with TestingSessionLocal() as session:
            service = RecurringTransactionExecutionService(session)

            count = await service.process_due_transactions(date(2026, 1, 1))

        transactions = await get_transactions()
        recurring = await get_recurring_transaction(recurring_id)

        assert count == 0
        assert len(transactions) == 0
        assert recurring.next_run_date == date(2026, 1, 1)

    asyncio.run(run_test())


# -----------------------------------------
# NEXT RUN DATE CALCULATIONS
# -----------------------------------------


@pytest.mark.parametrize(
    "current_date, frequency, expected_date",
    [
        (
            date(2026, 1, 1),
            "daily",
            date(2026, 1, 2),
        ),
        (
            date(2026, 1, 1),
            "weekly",
            date(2026, 1, 8),
        ),
        (
            date(2026, 1, 31),
            "monthly",
            date(2026, 2, 28),
        ),
        (
            date(2026, 2, 28),
            "monthly",
            date(2026, 3, 31),
        ),
        (
            date(2024, 2, 29),
            "yearly",
            date(2025, 2, 28),
        ),
    ],
)
def test_calculate_next_run_date(
    current_date,
    frequency,
    expected_date,
):

    repository = RecurringTransactionExecutionRepository(None)

    result = repository.calculate_next_run_date(
        current_date,
        frequency,
    )

    assert result == expected_date
