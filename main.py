from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.transaction import Transaction

from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.repositories.transaction import TransactionRepository
from app.services.transaction import TransactionService

app = FastAPI()


def get_transaction_service(
    session: AsyncSession = Depends(get_db),
) -> TransactionService:
    repository = TransactionRepository(session)
    return TransactionService(repository)


@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API"}


@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.create_transaction(transaction.model_dump(mode="json"))


@app.get("/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.get_transactions()
