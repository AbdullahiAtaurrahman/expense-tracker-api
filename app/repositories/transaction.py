from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(self, transaction_data: dict) -> Transaction:

        transaction = Transaction(**transaction_data)

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

    async def get_transactions(self) -> list[Transaction]:
        result = await self.session.execute(select(Transaction))

        return list(result.scalars().all())

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )

        return result.scalar_one_or_none()
