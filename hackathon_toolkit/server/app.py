from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from server.bunqService import BunqService
from server.midnightSweeper import MidnightSweeper
from server.lifestyleArbitrage import LifestyleArbitrage
from server.taxLedgerAgent import TaxLedgerAgent
from server.habitEnforcer import HabitEnforcer

app = FastAPI(
    title="A1 Financial Copilot",
    description="bunq Hackathon MVP with bunq sandbox API and Claude AI",
    version="1.0.0",
)


class PaymentRequest(BaseModel):
    amount: str
    description: str


class LifestyleRequest(BaseModel):
    productName: str
    priceOptions: str
    targetCurrency: str = "EUR"


class LedgerRequest(BaseModel):
    paymentId: int
    receiptText: str


class HabitRequest(BaseModel):
    goal: str
    proofText: str
    amount: str = "10.00"


@app.get("/")
def home():
    return {
        "message": "A1 Financial Copilot backend is running",
        "features": [
            "bunq transactions",
            "Midnight Liquidity Sweeper",
            "Lifestyle Arbitrageur",
            "Tax & Ledger Agent",
            "Habit Enforcer",
        ],
    }


@app.get("/api/bunq/accounts")
def get_accounts():
    service = BunqService()
    return service.get_accounts()


@app.get("/api/bunq/transactions")
def get_transactions():
    service = BunqService()
    return service.get_transactions()


@app.get("/api/bunq/transactions/{payment_id}")
def get_transaction_detail(payment_id: int):
    try:
        service = BunqService()
        transaction = service.get_transaction_by_id(payment_id)

        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return transaction

    except Exception as error:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction not found or bunq error: {str(error)}",
        )


@app.post("/api/bunq/request-money")
def request_money(request: PaymentRequest):
    service = BunqService()
    result = service.request_test_money(
        amount=request.amount,
        description=request.description,
    )

    return {
        "message": "Payment request created",
        "result": result,
    }


@app.post("/api/bunq/send-payment")
def send_payment(request: PaymentRequest):
    service = BunqService()
    result = service.send_test_payment(
        amount=request.amount,
        description=request.description,
    )

    return {
        "message": "Payment sent",
        "result": result,
    }


@app.post("/api/bunq/create-savings-account")
def create_savings_account():
    service = BunqService()
    result = service.create_savings_account()

    return {
        "message": "Savings account created",
        "result": result,
    }


@app.get("/api/ai/midnight-sweeper")
def midnight_sweeper():
    service = BunqService()
    transactions = service.get_transactions()

    accounts = service.get_accounts()
    current_balance = "0.00"

    if accounts:
        current_balance = accounts[0].get("balance", "0.00")

    sweeper = MidnightSweeper()
    ai_result = sweeper.analyze_liquidity(
        transactions=transactions,
        current_balance=current_balance,
    )

    return {
        "feature": "Midnight Liquidity Sweeper",
        "currentBalance": current_balance,
        "aiResult": ai_result,
    }


@app.post("/api/ai/lifestyle-arbitrage")
def lifestyle_arbitrage(request: LifestyleRequest):
    arbitrage = LifestyleArbitrage()

    ai_result = arbitrage.analyze_purchase(
        product_name=request.productName,
        user_prices=request.priceOptions,
    )

    virtual_card_demo = arbitrage.build_virtual_card_demo_response(
        target_currency=request.targetCurrency,
    )

    return {
        "feature": "Lifestyle Arbitrageur",
        "aiResult": ai_result,
        "bunqDemoAction": virtual_card_demo,
    }


@app.post("/api/ai/tax-ledger")
def tax_ledger(request: LedgerRequest):
    bunq = BunqService()
    transaction = bunq.get_transaction_by_id(request.paymentId)

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    agent = TaxLedgerAgent()

    ledger_note = agent.create_ledger_entry(
        receipt_text=request.receiptText,
        transaction_detail=transaction,
    )

    return {
        "feature": "Real-time Tax & Ledger Agent",
        "transaction": transaction,
        "ledgerNote": ledger_note,
    }


@app.post("/api/ai/habit-enforcer")
def habit_enforcer(request: HabitRequest):
    agent = HabitEnforcer()
    ai_result = agent.evaluate_habit(
        goal=request.goal,
        proof_text=request.proofText,
    )

    return {
        "feature": "Habit Enforcer",
        "aiResult": ai_result,
        "sandboxActionOptions": {
            "successAction": "Use POST /api/bunq/request-money as a reward demo",
            "failedAction": "Use POST /api/bunq/send-payment as a charity penalty demo",
            "amount": request.amount,
        },
    }