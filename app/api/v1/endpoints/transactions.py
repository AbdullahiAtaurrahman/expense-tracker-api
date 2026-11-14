from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user

from app.database import get_db
from app.models.user import User

from datetime import datetime


from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    TransactionType,
    TransactionResponse,
    TransactionSummary,
)
from app.repositories.transaction import TransactionRepository
from app.services.transaction import TransactionService

router = APIRouter()


def get_transaction_service(
    session: AsyncSession = Depends(get_db),
) -> TransactionService:
    return TransactionService(session)


@router.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API"}


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_transaction(
        transaction.model_dump(mode="json"), current_user.id
    )


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    transaction_type: TransactionType | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = TransactionService(session)

    return await service.get_transactions(
        user_id=current_user.id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    transaction = await service.update_transaction(
        transaction_id, transaction_data, current_user.id
    )

    if transaction is None:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    return transaction


@router.get(
    "/transactions/summary",
    response_model=TransactionSummary,
)
async def get_transaction_summary(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_transaction_summary(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user),
):
    transaction = await service.get_transaction_by_id(transaction_id, current_user.id)

    if transaction is None:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    return transaction


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user),
):
    transaction = await service.delete_transaction(transaction_id, current_user.id)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
