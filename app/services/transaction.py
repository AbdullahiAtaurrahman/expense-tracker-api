from app.repositories.transaction import TransactionRepository
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionUpdate


class TransactionService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    async def create_transaction(self, transaction_data: dict) -> Transaction:
        return await self.repository.create_transaction(transaction_data)

    async def get_transactions(self) -> list[Transaction]:
        return await self.repository.get_transactions()

    async def update_transaction(
        self, transaction_id: int, transaction_data: TransactionUpdate
    ):
        return await self.repository.update_transaction(
            transaction_id, transaction_data.model_dump(exclude_unset=True)
        )

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        return await self.repository.get_transaction_by_id(transaction_id)

    async def delete_transaction(self, transaction_id: int) -> Transaction | None:
        return await self.repository.delete_transaction(transaction_id)
