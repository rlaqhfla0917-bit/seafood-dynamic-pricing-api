from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, Seafood
from ..schemas import OrderCreate, OrderStatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["Order"])

def serialize(order: Order):
    return {
        "order_id": order.id,
        "seafood_id": order.seafood_id,
        "quantity": order.quantity,
        "status": order.status,
    }

@router.post("", status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    item = db.get(Seafood, payload.seafood_id)
    if not item:
        raise HTTPException(404, "상품을 찾을 수 없습니다")

    if item.status in ("SOLD_OUT", "CLOSED"):
        raise HTTPException(409, "판매할 수 없는 상품입니다")

    if item.stock_quantity < payload.quantity:
        raise HTTPException(status_code=409, detail={"error": "재고 부족", "code": 409})

    item.stock_quantity -= payload.quantity
    if item.stock_quantity == 0:
        item.status = "SOLD_OUT"

    order = Order(
        seafood_id=payload.seafood_id,
        quantity=payload.quantity,
        status="ORDERED",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return serialize(order)

@router.get("")
def list_orders(
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return [serialize(x) for x in orders]

@router.patch("/{order_id}/status")
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "주문을 찾을 수 없습니다")

    order.status = payload.status.value
    db.commit()
    db.refresh(order)
    return serialize(order)
