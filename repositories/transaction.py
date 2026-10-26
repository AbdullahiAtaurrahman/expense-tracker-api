class TransactionRepository:
    def __init__(self):
        self.transactions = []
        self.next_id = 1

    def create_transaction(self, transaction_data: dict) -> dict:

        transaction = {"id": self.next_id, **transaction_data}

        self.transactions.append(transaction)
        self.next_id += 1

        return transaction

    def get_transactions(self) -> list:
        return self.transactions
