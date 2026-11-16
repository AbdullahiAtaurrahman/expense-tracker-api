import calendar
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction


class RecurringTransactionExecutionRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    def calculate_next_run_date(
        self,
        current_date: date,
        frequency: str,
    ) -> date:

        if frequency == "daily":
            return current_date + timedelta(days=1)

        if frequency == "weekly":
            return current_date + timedelta(weeks=1)

        if frequency == "monthly":

            next_month = current_date.month + 1
            next_year = current_date.year

            if next_month > 12:
                next_month = 1
                next_year += 1

            current_month_last_day = calendar.monthrange(
                current_date.year,
                current_date.month,
            )[1]

            next_month_last_day = calendar.monthrange(
                next_year,
                next_month,
            )[1]

            if current_date.day == current_month_last_day:
                next_day = next_month_last_day
            else:
                next_day = min(
                    current_date.day,
                    next_month_last_day,
                )

            return date(next_year, next_month, next_day)

        if frequency == "yearly":

            next_year = current_date.year + 1

            next_day = min(
                current_date.day,
                calendar.monthrange(
                    next_year,
                    current_date.month,
                )[1],
            )

            return date(
                next_year,
                current_date.month,
                next_day,
            )

        raise ValueError("Unsupported recurrence frequency")

    async def process_due_transactions(
        self,
        today: date,
    ) -> int:

        processed_count = 0

        try:
            result = await self.session.execute(
                select(RecurringTransaction)
                .where(
                    RecurringTransaction.is_active.is_(True),
                    RecurringTransaction.next_run_date <= today,
                )
                .order_by(RecurringTransaction.next_run_date.asc())
                .with_for_update(skip_locked=True)
            )

            recurring_transactions = result.scalars().all()

            for recurring in recurring_transactions:

                while recurring.next_run_date <= today and recurring.is_active:

                    scheduled_date = recurring.next_run_date

                    if recurring.end_date and scheduled_date > recurring.end_date:
                        recurring.is_active = False
                        break

                    statement = (
                        insert(Transaction)
                        .values(
                            user_id=recurring.user_id,
                            amount=recurring.amount,
                            transaction_type=recurring.transaction_type,
                            purpose=recurring.purpose,
                            category=recurring.category,
                            recurring_transaction_id=recurring.id,
                            recurrence_date=scheduled_date,
                        )
                        .on_conflict_do_nothing(
                            constraint="uq_transaction_recurring_date"
                        )
                    )

                    result = await self.session.execute(statement)

                    if result.rowcount and result.rowcount > 0:
                        processed_count += 1

                    recurring.next_run_date = self.calculate_next_run_date(
                        scheduled_date,
                        recurring.frequency,
                    )

                    if (
                        recurring.end_date
                        and recurring.next_run_date > recurring.end_date
                    ):
                        recurring.is_active = False

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

        return processed_count
