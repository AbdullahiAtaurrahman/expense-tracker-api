from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.transaction import Transaction

from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.schemas.transaction import TransactionUpdate
from app.repositories.transaction import TransactionRepository
from app.services.transaction import TransactionService

router = APIRouter()


def get_transaction_service(
    session: AsyncSession = Depends(get_db),
) -> TransactionService:
    repository = TransactionRepository(session)
    return TransactionService(repository)


@router.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API"}


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.create_transaction(transaction.model_dump(mode="json"))


@router.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.get_transactions()


@router.patch("transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
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
):
    transaction = await service.get_transaction_by_id(transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=404, detail=f"Transaction with ID {transaction_id} not found"
        )

    return transaction


@router.delete("/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: int, service: TransactionService = Depends(get_transaction_service)
):
    transaction = await service.delete_transaction(transaction_id)

    if transaction is None:
        raise HTTPException(status_code=202, detail=f"No Content")
