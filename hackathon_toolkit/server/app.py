from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from server.bunqService import BunqService

app = FastAPI()


class PaymentRequest(BaseModel):
    amount: str
    description: str


@app.get("/")
def home():
    return {
        "message": "bunq backend is running"
    }


@app.get("/api/bunq/transactions")
def get_transactions():
    service = BunqService()
    return service.get_transactions()


@app.get("/api/bunq/transactions/{payment_id}")
def get_transaction_detail(payment_id: int):
    service = BunqService()
    transaction = service.get_transaction_by_id(payment_id)

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@app.post("/api/bunq/request-money")
def request_money(request: PaymentRequest):
    service = BunqService()
    result = service.create_payment_request(
        amount=request.amount,
        description=request.description,
    )

    return {
        "message": "Payment request created",
        "result": result,
    }