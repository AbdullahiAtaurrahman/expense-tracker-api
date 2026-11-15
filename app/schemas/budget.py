from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=9999)


class BudgetUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=100)
    amount: float | None = Field(default=None, gt=0)


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    amount: float
    month: int
    year: int

    model_config = ConfigDict(from_attributes=True)


class BudgetSummary(BaseModel):
    category: str
    budget_amount: float
    spent: float
    remaining: float
    percentage_used: float
    status: str
