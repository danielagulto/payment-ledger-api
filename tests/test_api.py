from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_customer_plan_payment_flow():
    import uuid
    email = f"{uuid.uuid4()}@example.com"
    customer = client.post("/customers", json={"full_name":"Test Customer","email":email})
    assert customer.status_code == 201
    plan = client.post("/payment-plans", json={
        "customer_id": customer.json()["id"], "total_cents": 10000, "installments": 4
    })
    assert plan.status_code == 201
    plan_id = plan.json()["id"]
    payment = client.post("/payments", headers={"Idempotency-Key": f"test-{uuid.uuid4()}"},
                          json={"plan_id": plan_id, "amount_cents": 2500})
    assert payment.status_code == 201
    balance = client.get(f"/payment-plans/{plan_id}").json()
    assert balance["paid_cents"] == 2500
    assert balance["remaining_cents"] == 7500
