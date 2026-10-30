from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.transaction import Transaction

from app.api.v1.router import router as v1_router

from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.repositories.transaction import TransactionRepository
from app.services.transaction import TransactionService

app = FastAPI()


app.include_router(v1_router, prefix="/api/v1")
