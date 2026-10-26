from repositories.transaction import TransactionRepository


class TransactionService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    def create_transaction(self, transaction_data: dict) -> dict:
        return self.repository.create_transaction(transaction_data)

    def get_transactions(self) -> list[dict]:
        return self.repository.get_transactions()
