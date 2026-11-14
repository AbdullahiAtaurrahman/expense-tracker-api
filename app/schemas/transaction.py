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
    category: str | None = None


class TransactionResponse(TransactionCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    category: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    transaction_type: TransactionType | None = None
    purpose: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = None


class TransactionSummary(BaseModel):
    total_income: int
    total_expenses: int
    balance: float
    total_transactions: int
    income_transactions: int
    expense_transactions: int


class MonthlyTransactionSummary(BaseModel):
    month: str
    total_income: float
    total_expenses: float
    balance: float
    income_transactions: int
    expense_transactions: int
    total_transactions: int


class CategorySpendingSummary(BaseModel):
    category: str
    total_spent: str
    transaction_count: int
    percentage: float
