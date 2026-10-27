from app.repositories.transaction import TransactionRepository
from app.models.transaction import Transaction


class TransactionService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    async def create_transaction(self, transaction_data: dict) -> Transaction:
        return await self.repository.create_transaction(transaction_data)

    async def get_transactions(self) -> list[Transaction]:
        return await self.repository.get_transactions()
