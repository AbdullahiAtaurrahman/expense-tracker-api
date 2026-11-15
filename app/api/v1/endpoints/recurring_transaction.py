from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionResponse,
    RecurringTransactionUpdate,
)

from app.services.recurring_transaction import RecurringTransactionService

from app.api.dependencies import get_current_user

router = APIRouter(
    prefix="/recurring-transactions",
    tags=["Recurring Transactions"],
)


def get_recurring_transaction_service(
    session: AsyncSession = Depends(get_db),
):
    return RecurringTransactionService(session)


@router.post(
    "", response_model=RecurringTransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_recurring_transaction(
    transaction_data: RecurringTransactionCreate,
    service: RecurringTransactionService = Depends(get_recurring_transaction_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_recurring_transaction(transaction_data, current_user.id)


@router.get("", response_model=list[RecurringTransactionResponse])
async def get_recurring_transactions(
    service: RecurringTransactionService = Depends(get_recurring_transaction_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_recurring_transactions(current_user.id)


@router.get(
    "/{transaction_id}",
    response_model=RecurringTransactionResponse,
)
async def get_recurring_transaction_by_id(
    transaction_id: int,
    service: RecurringTransactionService = Depends(get_recurring_transaction_service),
    current_user: User = Depends(get_current_user),
):
    transaction = await service.get_recurring_transaction_by_id(
        transaction_id, current_user.id
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction with {transaction_id} not found",
        )

    return transaction


@router.patch("/{transaction_id}", response_model=RecurringTransactionResponse)
async def update_recurring_transaction(
    transaction_id: int,
    transaction_data: RecurringTransactionUpdate,
    service: RecurringTransactionService = Depends(get_recurring_transaction_service),
    current_user: User = Depends(get_current_user),
):
    transaction = await service.update_recurring_transaction(
        transaction_id, transaction_data, current_user.id
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction with ID {transaction_id} not found",
        )

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_transaction(
    transaction_id: int,
    service: RecurringTransactionService = Depends(get_recurring_transaction_service),
    current_user: User = Depends(get_current_user),
):
    deleted = await service.delete_recurring_transaction(
        transaction_id, current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recurring transaction with ID {transaction_id} not found",
        )
