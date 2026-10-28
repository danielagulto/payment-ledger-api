from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str

class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    created_at: datetime

class PlanCreate(BaseModel):
    customer_id: int
    total_cents: int = Field(gt=0)
    installments: int = Field(ge=1, le=60)

class PaymentCreate(BaseModel):
    plan_id: int
    amount_cents: int = Field(gt=0)

class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plan_id: int
    amount_cents: int
    status: str
    idempotency_key: str
    simulated: bool
    created_at: datetime
