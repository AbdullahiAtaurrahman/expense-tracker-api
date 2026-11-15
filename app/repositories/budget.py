from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_budget(self, budget_data: BudgetCreate, user_id: int):
        budget = Budget(**budget_data.model_dump(), user_id=user_id)

        self.session.add(budget)

        try:
            await self.session.commit()
            await self.session.refresh(budget)
        except:
            await self.session.rollback()
            raise ValueError("A budget already exists for this category and month")

        return budget

    async def get_budgets(self, user_id: int, month: int | None, year: int | None):
        query = select(Budget).where(Budget.user_id == user_id)

        if month is not None:
            query = query.where(Budget.month == month)

        if year is not None:
            query = query.where(Budget.year == year)

        result = await self.session.execute(
            query.order_by(Budget.year.desc(), Budget.month.desc())
        )

        return result.scalars().all()

    async def get_budget_by_id(self, budget_id: int, user_id: int):
        result = await self.session.execute(
            select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        )

        return result.scalar_one_or_none()

    async def update_budget(self, budget_id: int, budget_data, user_id: int):
        budget = await self.session.get_budget_by_id(budget_id, user_id)

        if not budget:
            return None

        updata_data = budget_data.model_dump(exclude_unset=True)

        for key, value in updata_data.items():
            setattr(budget, key, value)

        try:
            await self.session.commit()
            await self.session.refresh(budget)

        except:
            await self.session.rollback()
            raise ValueError("A budget already exists for this category and month")

        return budget

    async def delete_budget(
        self,
        budget_id: int,
        user_id: int,
    ):
        budget = await self.get_budget_by_id(budget_id, user_id)

        if not budget:
            return None

        await self.session.delete(budget)
        await self.session.commit()

        return True

    async def get_budget_spending(
        self,
        user_id: int,
        month: int,
        year: int,
    ):
        start_date = datetime(year, month, 1, tzinfo=timezone.utc + 1)

        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc + 1)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc + 1)

        result = await self.session.execute(
            select(
                Transaction.category,
                func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
                Transaction.created_at >= start_date,
                Transaction.created_at < end_date,
            )
            .group_by(Transaction.category)
        )

        return {row.category: float(row.spent) for row in result.all()}
