from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User

from app.schemas.budget import BudgetUpdate, BudgetCreate, BudgetResponse, BudgetSummary

from app.services.budget import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def get_budget_service(session: AsyncSession = Depends(get_db)):
    return BudgetService(session)


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user),
):
    try:
        return await service.create_budget(
            budget_data,
            current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "",
    response_model=list[BudgetResponse],
)
async def get_budgets(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=9999),
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_budgets(
        current_user.id,
        month,
        year,
    )


@router.get(
    "/summary",
    response_model=list[BudgetSummary],
)
async def get_budget_summary(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=9999),
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_budget_summary(
        current_user.id,
        month,
        year,
    )


@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
)
async def get_budget(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user),
):
    budget = await service.get_budget_by_id(
        budget_id,
        current_user.id,
    )

    if not budget:
        raise HTTPException(
            status_code=404,
            detail=f"Budget with ID {budget_id} not found",
        )

    return budget


@router.patch(
    "/{budget_id}",
    response_model=BudgetResponse,
)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user),
):
    try:
        budget = await service.update_budget(
            budget_id,
            budget_data,
            current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    if not budget:
        raise HTTPException(
            status_code=404,
            detail=f"Budget with ID {budget_id} not found",
        )

    return budget


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_budget(
    budget_id: int,
    service: BudgetService = Depends(get_budget_service),
    current_user: User = Depends(get_current_user),
):
    deleted = await service.delete_budget(
        budget_id,
        current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Budget with ID {budget_id} not found",
        )
