from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RecurringTransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    transaction_type: Literal["income", "expense"]
    purpose: str = Field(min_length=1)
    category: str | None = Field(default=None, max_length=100)
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")

        return self


class RecurringTransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, get=0)

    purpose: str | None = Field(default=None, min_length=1)

    category: str | None = Field(default=None, max_length=100)

    frequency: Literal["daily", "weekly", "monthly", "yearly"] | None = None

    end_date: date | None = None

    is_active: bool | None = None


class RecurringTransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    purpose: str
    category: str | None
    frequency: str
    start_date: date
    end_date: date | None
    next_run_date: date
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
