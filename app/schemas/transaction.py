from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    transaction_type: TransactionType
    purpose: str = Field(min_length=1, max_length=200)


class TransactionResponse(TransactionCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    transaction_type: TransactionType | None = None
    purpose: str | None = Field(default=None, min_length=1, max_length=200)
