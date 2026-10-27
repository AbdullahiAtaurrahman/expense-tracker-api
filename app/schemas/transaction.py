from enum import Enum

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

    model_config = ConfigDict(from_attributes=True)
