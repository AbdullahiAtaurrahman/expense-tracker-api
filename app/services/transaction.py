from app.repositories.transaction import TransactionRepository
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionUpdate
from app.schemas.transaction import TransactionType

from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.repository = TransactionRepository(session)

    async def create_transaction(
        self, transaction_data: dict, user_id: int
    ) -> Transaction:
        return await self.repository.create_transaction(transaction_data, user_id)

    async def get_transactions(
        self,
        user_id: int,
        transaction_type: TransactionType | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        sort_by: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 10,
    ):
        return await self.repository.get_transactions(
            user_id=user_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            order=order,
            skip=skip,
            limit=limit,
        )

    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data: TransactionUpdate,
        user_id: int,
    ) -> Transaction | None:
        return await self.repository.update_transaction(
            transaction_id,
            transaction_data.model_dump(exclude_unset=True),
            user_id,
        )

    async def get_transaction_by_id(
        self, transaction_id: int, user_id: int
    ) -> Transaction | None:
        return await self.repository.get_transaction_by_id(transaction_id, user_id)

    async def delete_transaction(
        self, transaction_id: int, user_id: int
    ) -> Transaction | None:
        return await self.repository.delete_transaction(transaction_id, user_id)

    async def get_transaction_summary(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        return await self.repository.get_transaction_summary(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_monthly_analytics(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        return await self.repository.get_monthly_analytics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

    async def get_category_spending(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):

        return await self.repository.get_category_spending(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
