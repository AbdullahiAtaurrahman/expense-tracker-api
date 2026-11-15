from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.budget import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetService:

    def __init__(self, session: AsyncSession):
        self.repository = BudgetRepository(session)

    async def create_budget(self, budget_data: BudgetCreate, user_id: int):
        return await self.repository.create_budget(budget_data, user_id)

    async def get_budgets(
        self,
        user_id: int,
        month: int | None = None,
        year: int | None = None,
    ):
        return await self.repository.get_budgets(
            user_id,
            month,
            year,
        )

    async def get_budget_by_id(
        self,
        budget_id: int,
        user_id: int,
    ):
        return await self.repository.get_budget_by_id(
            budget_id,
            user_id,
        )

    async def update_budget(
        self,
        budget_id: int,
        budget_data: BudgetUpdate,
        user_id: int,
    ):
        return await self.repository.update_budget(
            budget_id,
            budget_data,
            user_id,
        )

    async def delete_budget(
        self,
        budget_id: int,
        user_id: int,
    ):
        return await self.repository.delete_budget(
            budget_id,
            user_id,
        )

    async def get_budget_summary(
        self,
        user_id: int,
        month: int | None = None,
        year: int | None = None,
    ):
        now = datetime.now(timezone.utc + 1)

        month = month or now.month
        year = year or now.year

        budgets = await self.repository.get_budgets(
            user_id,
            month,
            year,
        )

        spending = await self.repository.get_budget_spending(
            user_id,
            month,
            year,
        )

        summaries = []

        for budget in budgets:
            spent = spending.get(budget.category, 0.0)

            remaining = budget.amount - spent

            percentage_used = (spent / budget.amount) * 100

            if percentage_used > 100:
                status = "exceeded"
            elif percentage_used >= 80:
                status = "near_limit"
            else:
                status = "within_budget"

            summaries.append(
                {
                    "category": budget.category,
                    "budget_amount": budget.amount,
                    "spent": spent,
                    "remaining": remaining,
                    "percentage_used": round(percentage_used, 2),
                    "status": status,
                }
            )

        return summaries
