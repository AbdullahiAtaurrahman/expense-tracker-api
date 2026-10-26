from fastapi import FastAPI
from schemas.transaction import TransactionCreate
from repositories.transaction import TransactionRepository
from services.transaction import TransactionService

app = FastAPI()

repository = TransactionRepository()
service = TransactionService(repository)


@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API"}


@app.post("/transactions")
def create_transaction(transaction: TransactionCreate):
    transaction_data = transaction.model_dump(mode="json")
    return service.create_transaction(transaction_data)


@app.get("/transactions")
def get_transactions():
    return service.get_transactions()
