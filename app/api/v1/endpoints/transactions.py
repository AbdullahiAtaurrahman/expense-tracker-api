from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import float, ForeignKey, Integer, String


from app.api.dependencies import get_current_user

from app.database import get_db
from app.models.transaction import Transaction
from app.models.user import User


from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.transaction import TransactionUpdate
from app.repositories.transaction import TransactionRepository
from app.services.transaction import TransactionService

router = APIRouter()


def get_transaction_service(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionService:
    repository = TransactionRepository(session)
    return TransactionService(repository)


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
    status_code=status.HTTP_202_ACCEPTED,
    current_user: User = Depends(get_current_user),
):
    return await service.create_transaction(transaction.model_dump(mode="json"))


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    service: TransactionService = Depends(get_transaction_service),
    status_code=status.HTTP_200_OK,
    current_user: User = Depends(get_current_user),
):
    return await service.get_transactions()


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
    transaction = await service.update_transaction(transaction_id, transaction_data)

    if transaction is None:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    return transaction


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction_by_id(
    transaction_id: int,
    service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user),
):
    transaction = await service.get_transaction_by_id(transaction_id)

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
    transaction = await service.delete_transaction(transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
