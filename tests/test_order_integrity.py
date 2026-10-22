"""Regression coverage for stock reservation, cancellation and status safety."""
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def make_item(stock=2, status="ON_SALE"):
    response = client.post("/api/v1/seafoods", json={
        "name": "테스트 수산물", "category": "FISH", "base_price": 10000,
        "stock_quantity": stock, "freshness_grade": "A",
        "catch_amount": 50, "status": status,
    })
    assert response.status_code == 201
    return response.json()["seafood_id"]

def order(sid, qty):
    return client.post("/api/v1/orders", json={"seafood_id": sid, "quantity": qty})

def test_reserved_stock_cannot_be_oversold_and_cancel_restores_once():
    sid = make_item(2)
    first = order(sid, 2)
    assert first.status_code == 201
    oid = first.json()["order_id"]
    assert client.get(f"/api/v1/seafoods/{sid}").json()["status"] == "SOLD_OUT"
    assert order(sid, 1).status_code == 409
    assert client.patch(f"/api/v1/orders/{oid}/status", json={"status": "CANCELED"}).status_code == 200
    item = client.get(f"/api/v1/seafoods/{sid}").json()
    assert item["stock_quantity"] == 2
    assert item["status"] == "ON_SALE"
    assert client.patch(f"/api/v1/orders/{oid}/status", json={"status": "CANCELED"}).status_code == 409
    assert client.get(f"/api/v1/seafoods/{sid}").json()["stock_quantity"] == 2

def test_shipped_order_cannot_cancel():
    sid = make_item(1)
    oid = order(sid, 1).json()["order_id"]
    for status in ("PAID", "PACKING", "SHIPPED"):
        assert client.patch(f"/api/v1/orders/{oid}/status", json={"status": status}).status_code == 200
    assert client.patch(f"/api/v1/orders/{oid}/status", json={"status": "CANCELED"}).status_code == 409
    assert client.get(f"/api/v1/seafoods/{sid}").json()["stock_quantity"] == 0

def test_closed_item_is_not_sellable():
    sid = make_item(3, "CLOSED")
    assert order(sid, 1).status_code == 409
    assert client.get(f"/api/v1/seafoods/{sid}").json()["stock_quantity"] == 3

def test_invalid_order_quantity_rejected():
    sid = make_item(3)
    assert order(sid, 0).status_code == 422
    assert order(sid, -1).status_code == 422
