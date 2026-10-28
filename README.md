# Payment Ledger API

REST API that simulates installment payments and maintains a transaction ledger. It does not move real money or connect to a payment processor.

## Features
- FastAPI endpoints for customers, payment plans, and payments
- SQLite persistence through SQLAlchemy
- Idempotency key support to prevent duplicate payment records on retries
- Validation, API docs, health endpoint, and pytest test
- Dockerfile

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs.

## Example
Create a customer (`POST /customers`), create a plan (`POST /payment-plans`), then submit a payment (`POST /payments`) with an `Idempotency-Key` header. Inspect the balance with `GET /payment-plans/{plan_id}`.

Demo only: use fictional data; not production-ready financial infrastructure.
