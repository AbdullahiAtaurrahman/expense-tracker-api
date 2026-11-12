from app.repositories.transaction import TransactionRepository
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionUpdate
from app.schemas.transaction import TransactionType


class TransactionService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    async def create_transaction(
        self, transaction_data: dict, user_id: int
    ) -> Transaction:
        return await self.repository.create_transaction(transaction_data, user_id)

    async def get_transactions(
        self, user_id: int, transaction_type: TransactionType | None = None
    ) -> list[Transaction]:
        return await self.repository.get_transactions(
            user_id=user_id, transaction_type=transaction_type
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
