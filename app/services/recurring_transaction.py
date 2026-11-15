from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.recurring_transaction import RecurringTransactionRepository


class RecurringTransactionService:

    def __init__(self, session: AsyncSession):
        self.repository = RecurringTransactionRepository(session)

    async def create_recurring_transaction(self, transaction_data, user_id: int):

        return await self.repository.create_recurring_transaction(
            transaction_data,
            user_id,
        )

    async def get_recurring_transactions(self, user_id: int):

        return await self.repository.get_recurring_transactions(
            user_id,
        )

    async def get_recurring_transaction_by_id(self, transaction_id: int, user_id: int):

        return await self.repository.get_recurring_transaction_by_id(
            transaction_id,
            user_id,
        )

    async def update_recurring_transaction(
        self, transaction_id: int, transaction_data, user_id: int
    ):

        return await self.repository.update_recurring_transaction(
            transaction_id,
            transaction_data,
            user_id,
        )

    async def delete_recurring_transaction(self, transaction_id: int, user_id: int):

        return await self.repository.delete_recurring_transaction(
            transaction_id,
            user_id,
        )
