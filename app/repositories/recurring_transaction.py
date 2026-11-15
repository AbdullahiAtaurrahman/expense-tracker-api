from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_transaction import RecurringTransaction


class RecurringTransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_recurring_transaction(self, transaction_data, user_id):
        transaction = RecurringTransaction(
            **transaction_data.model_dump(),
            user_id=user_id,
            next_run_date=transaction_data.start_date
        )

        self.session.add(transaction)

        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

    async def get_recurring_transactions(self, user_id):
        result = await self.session.execute(
            select(RecurringTransaction)
            .where(RecurringTransaction.user_id == user_id)
            .order_by(RecurringTransaction.created_at.desc())
        )

        return result.scalars().all()

    async def get_recurring_transaction_by_id(
        self,
        transaction_id,
        user_id,
    ):

        result = await self.session.execute(
            select(RecurringTransaction).where(
                RecurringTransaction.id == transaction_id,
                RecurringTransaction.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def update_recurring_transaction(
        self, transaction_id, transaction_data, user_id
    ):

        transaction = await self.get_recurring_transaction_by_id(
            transaction_id, user_id
        )

        if transaction is None:
            return None

        update_data = transaction_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(transaction, key, value)

        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

    async def delete_recurring_transaction(self, transaction_id: int, user_id: int):
        transaction = await self.get_recurring_transaction_by_id(
            transaction_id, user_id
        )

        if transaction is None:
            return False

        await self.session.delete(transaction)
        await self.session.commit()

        return True
