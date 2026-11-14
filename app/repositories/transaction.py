from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionType

from datetime import datetime


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(
        self, transaction_data: dict, user_id: int
    ) -> Transaction:

        transaction = Transaction(**transaction_data, user_id=user_id)

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

    async def update_transaction(
        self, transaction_id: int, transaction_data: dict, user_id: int
    ) -> Transaction | None:

        transaction = await self.get_transaction_by_id(transaction_id, user_id)

        if transaction is None:
            return None

        for key, value in transaction_data.items():
            setattr(transaction, key, value)

        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

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
    ) -> list[Transaction]:

        query = select(Transaction).where(Transaction.user_id == user_id)

        if transaction_type is not None:
            query = query.where(Transaction.transaction_type == transaction_type)

        if start_date is not None:
            query = query.where(Transaction.created_at >= start_date)

        if end_date is not None:
            query = query.where(Transaction.created_at <= end_date)

        sort_columns = {
            "created_at": Transaction.created_at,
            "amount": Transaction.amount,
        }

        sort_column = sort_columns.get(sort_by, Transaction.created_at)

        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)

        return result.scalars().all()

    async def get_transaction_by_id(
        self, transaction_id: int, user_id: int
    ) -> Transaction | None:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id, Transaction.user_id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def delete_transaction(
        self, transaction_id: int, user_id: int
    ) -> Transaction | None:

        result = await self.get_transaction_by_id(transaction_id, user_id)

        if result is None:
            return None

        await self.session.delete(result)
        await self.session.commit()

        return result

    async def get_transaction_summary(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:

        total_income = func.coalesce(
            func.sum(
                case(
                    (Transaction.transaction_type == "income", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        total_expenses = func.coalesce(
            func.sum(
                case(
                    (Transaction.transaction_type == "expense", Transaction.amount),
                    else_=0,
                )
            ),
            0,
        )

        income_transactions = func.count(
            case(
                (Transaction.transaction_type == "income", 1),
                else_=None,
            )
        )

        expense_transactions = func.count(
            case(
                (Transaction.transaction_type == "expense", 1),
                else_=None,
            )
        )

        query = select(
            total_income.label("total_income"),
            total_expenses.label("total_expenses"),
            func.count(Transaction.id).label("total_transactions"),
            income_transactions.label("income_transactions"),
            expense_transactions.label("expense_transactions"),
        ).where(Transaction.user_id == user_id)

        if start_date is not None:
            query = query.where(Transaction.created_at >= start_date)

        if end_date is not None:
            query = query.where(Transaction.created_at <= end_date)

        result = await self.session.execute(query)

        summary = result.one()

        income = float(summary.total_income)
        expenses = float(summary.total_expenses)

        return {
            "total_income": income,
            "total_expenses": expenses,
            "balance": income - expenses,
            "total_transactions": summary.total_transactions,
            "income_transactions": summary.income_transactions,
            "expense_transactions": summary.expense_transactions,
        }

    async def get_monthly_analytics(
        self,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list:
        month_column = func.to_char(
            func.date_trunc("month", Transaction.created_at), "YYYY-MM"
        )

        total_income = func.coalesce(
            func.sum(
                case(
                    (Transaction.transaction_type == "income", Transaction.amount),
                    else_=0,
                )
            )
        )

        total_expenses = func.coalesce(
            func.sum(
                case(
                    (Transaction.transaction_type == "expense", Transaction.amount),
                    else_=0,
                )
            )
        )

        income_transactions = func.count(
            case((Transaction.transaction_type == "income", 1), else_=None)
        )

        expense_transactions = func.count(
            case((Transaction.transaction_type == "expense", 1), else_=None)
        )

        query = select(
            month_column.label("month"),
            total_income.label("total_income"),
            total_expenses.label("total_expenses"),
            income_transactions.label("income_transactions"),
            expense_transactions.label("expense_transactions"),
            func.count(Transaction.id).label("total_transactions"),
        ).where(Transaction.user_id == user_id)

        if start_date is not None:
            query = query.where(Transaction.created_at >= start_date)

        if end_date is not None:
            query = query.where(Transaction.created_at <= end_date)

        query = query.group_by(month_column).order_by(month_column.asc())

        result = await self.session.execute(query)

        analytics = []

        for row in result:
            income = float(row.total_income)
            expenses = float(row.total_expenses)

            analytics.append(
                {
                    "month": row.month,
                    "total_income": income,
                    "total_expenses": expenses,
                    "balance": income - expenses,
                    "income_transactions": row.income_transactions,
                    "expense_transactions": row.expense_transactions,
                    "total_transactions": row.total_transactions,
                }
            )

        return analytics
