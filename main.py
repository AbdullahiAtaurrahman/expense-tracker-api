from fastapi import FastAPI
from schemas.transaction import TransactionCreate

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API"}


@app.post("/transactions")
def create_transaction(transaction: TransactionCreate):

    return {"message": "Transaction created successfully", "transaction": transaction}
