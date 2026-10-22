"""Order routes: atomic inventory reservations and controlled status transitions."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, update
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, Seafood
from ..schemas import OrderCreate, OrderStatus, OrderStatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["Order"])

SELLABLE = ("ON_SALE", "PRICE_UPDATED", "DISCOUNTED")
TRANSITIONS = {
    "ORDERED": {"PAID", "CANCELED"},
    "PAID": {"PACKING", "CANCELED"},
    "PACKING": {"SHIPPED", "CANCELED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": set(),
    "CANCELED": set(),
}


def serialize(order: Order):
    return {
        "order_id": order.id,
        "seafood_id": order.seafood_id,
        "quantity": order.quantity,
        "status": order.status,
    }


@router.post("", status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    # One conditional UPDATE is atomic even when multiple workers submit orders.
    # Reading stock then decrementing the ORM object can oversell under concurrency.
    result = db.execute(
        update(Seafood)
        .where(
            Seafood.id == payload.seafood_id,
            Seafood.status.in_(SELLABLE),
            Seafood.stock_quantity >= payload.quantity,
        )
        .values(
            stock_quantity=Seafood.stock_quantity - payload.quantity,
            status=case(
                (Seafood.stock_quantity == payload.quantity, "SOLD_OUT"),
                else_=Seafood.status,
            ),
        )
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        item = db.get(Seafood, payload.seafood_id)
        db.rollback()
        if not item:
            raise HTTPException(404, "상품을 찾을 수 없습니다")
        raise HTTPException(409, "판매 중이 아니거나 재고가 부족합니다")

    order = Order(
        seafood_id=payload.seafood_id,
        quantity=payload.quantity,
        status=OrderStatus.ORDERED.value,
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
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "주문을 찾을 수 없습니다")

    next_status = payload.status.value
    previous_status = order.status
    if next_status not in TRANSITIONS.get(previous_status, set()):
        raise HTTPException(409, "현재 주문 상태에서 허용되지 않는 변경입니다")

    # Compare-and-swap prevents a second request from canceling/restocking twice.
    result = db.execute(
        update(Order)
        .where(Order.id == order_id, Order.status == previous_status)
        .values(status=next_status)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "다른 요청에서 주문 상태가 변경되었습니다")

    if next_status == OrderStatus.CANCELED.value:
        # Never reopen deliberately CLOSED goods. SOLD_OUT becomes saleable
        # only when stock has been returned by a valid cancellation.
        db.execute(
            update(Seafood)
            .where(Seafood.id == order.seafood_id)
            .values(
                stock_quantity=Seafood.stock_quantity + order.quantity,
                status=case(
                    (Seafood.status == "SOLD_OUT", "ON_SALE"),
                    else_=Seafood.status,
                ),
            )
            .execution_options(synchronize_session=False)
        )
    db.commit()
    db.refresh(order)
    return serialize(order)
