from fastapi import APIRouter

from app.api.v1.endpoints import transactions
from app.api.v1.endpoints import budgets
from app.api.v1.endpoints import recurring_transaction
from app.api.v1.endpoints import auth

router = APIRouter()

router.include_router(transactions.router)
router.include_router(budgets.router)
router.include_router(recurring_transaction.router)
router.include_router(auth.router)
