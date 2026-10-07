import os
os.environ["DATABASE_URL"] = "sqlite:///./test_seafood.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health():
    assert client.get("/health").status_code == 200

def test_create_price_and_order_flow():
    create = client.post("/api/v1/seafoods", json={
        "name": "제주 고등어",
        "category": "FISH",
        "origin": "제주",
        "base_price": 20000,
        "unit": "kg",
        "stock_quantity": 60,
        "freshness_grade": "A",
        "catch_amount": 120,
        "status": "ON_SALE",
    })
    assert create.status_code == 201
    seafood_id = create.json()["seafood_id"]

    price = client.post(f"/api/v1/seafoods/{seafood_id}/price-calculate", json={
        "apply_freshness_rule": True,
        "apply_catch_rule": True,
        "apply_stock_rule": True,
        "apply_deadline_discount": False,
    })
    assert price.status_code == 200
    # 발표자료 응답 예시 기준: +20% -5% -10% = +5%
    assert price.json()["final_price"] == 21000

    order = client.post("/api/v1/orders", json={"seafood_id": seafood_id, "quantity": 1})
    assert order.status_code == 201

def test_insufficient_stock_returns_409():
    create = client.post("/api/v1/seafoods", json={
        "name": "오징어",
        "category": "OTHER",
        "base_price": 10000,
        "stock_quantity": 0,
        "freshness_grade": "B",
        "catch_amount": 20,
        "status": "ON_SALE",
    })
    seafood_id = create.json()["seafood_id"]
    response = client.post("/api/v1/orders", json={"seafood_id": seafood_id, "quantity": 1})
    assert response.status_code == 409
