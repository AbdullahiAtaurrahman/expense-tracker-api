from datetime import date

from app.repositories.recurring_transaction_execution import (
    RecurringTransactionExecutionRepository,
)


class RecurringTransactionExecutionService:

    def __init__(self, session):
        self.repository = RecurringTransactionExecutionRepository(session)

    async def process_due_transactions(
        self,
        today: date,
    ):
        return await self.repository.process_due_transactions(today)
