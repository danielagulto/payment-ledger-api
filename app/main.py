from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Payment Ledger API", version="1.0.0",
              description="Demo installment payment API. Payments are simulated; no real money moves.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "payment-ledger-api"}

def plan_summary(plan):
    paid = sum(p.amount_cents for p in plan.payments if p.status == "succeeded")
    return {"id": plan.id, "customer_id": plan.customer_id, "total_cents": plan.total_cents,
            "installments": plan.installments, "status": "paid" if paid >= plan.total_cents else plan.status,
            "paid_cents": paid, "remaining_cents": max(plan.total_cents - paid, 0)}

@app.post("/customers", response_model=schemas.CustomerOut, status_code=201)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Customer).where(models.Customer.email == payload.email.lower())):
        raise HTTPException(409, "A customer with this email already exists")
    customer = models.Customer(full_name=payload.full_name, email=payload.email.lower())
    db.add(customer); db.commit(); db.refresh(customer)
    return customer

@app.get("/customers", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Customer).order_by(models.Customer.id.desc())))

@app.post("/payment-plans", status_code=201)
def create_plan(payload: schemas.PlanCreate, db: Session = Depends(get_db)):
    if not db.get(models.Customer, payload.customer_id):
        raise HTTPException(404, "Customer not found")
    plan = models.PaymentPlan(customer_id=payload.customer_id, total_cents=payload.total_cents,
                              installments=payload.installments)
    db.add(plan); db.commit(); db.refresh(plan)
    return plan_summary(plan)

@app.get("/payment-plans")
def list_plans(db: Session = Depends(get_db)):
    return [plan_summary(p) for p in db.scalars(select(models.PaymentPlan).order_by(models.PaymentPlan.id.desc()))]

@app.get("/payment-plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.get(models.PaymentPlan, plan_id)
    if not plan: raise HTTPException(404, "Payment plan not found")
    return plan_summary(plan)

@app.post("/payments", response_model=schemas.PaymentOut, status_code=201)
def create_payment(payload: schemas.PaymentCreate,
                   idempotency_key: str = Header(alias="Idempotency-Key", min_length=4),
                   db: Session = Depends(get_db)):
    existing = db.scalar(select(models.Payment).where(models.Payment.idempotency_key == idempotency_key))
    if existing:
        return existing
    plan = db.get(models.PaymentPlan, payload.plan_id)
    if not plan: raise HTTPException(404, "Payment plan not found")
    summary = plan_summary(plan)
    if summary["remaining_cents"] <= 0: raise HTTPException(409, "Plan is already fully paid")
    if payload.amount_cents > summary["remaining_cents"]:
        raise HTTPException(422, "Payment exceeds remaining balance")
    payment = models.Payment(plan_id=payload.plan_id, amount_cents=payload.amount_cents,
                             idempotency_key=idempotency_key, status="succeeded", simulated=True)
    db.add(payment); db.commit(); db.refresh(payment)
    return payment

@app.get("/payments", response_model=list[schemas.PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Payment).order_by(models.Payment.id.desc())))
