from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PriceHistory, Seafood
from ..price_engine import calculate_price
from ..schemas import CatchUpdate, FreshnessUpdate, PriceCalculateRequest, SeafoodCreate

router = APIRouter(prefix="/api/v1/seafoods", tags=["Seafood"])

def serialize(item: Seafood):
    return {
        "seafood_id": item.id,
        "name": item.name,
        "category": item.category,
        "origin": item.origin,
        "base_price": item.base_price,
        "final_price": item.final_price,
        "unit": item.unit,
        "stock_quantity": item.stock_quantity,
        "freshness_grade": item.freshness_grade,
        "catch_amount": item.catch_amount,
        "status": item.status,
    }

@router.post("", status_code=201)
def create_seafood(payload: SeafoodCreate, db: Session = Depends(get_db)):
    item = Seafood(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)

@router.get("")
def list_seafoods(
    freshness: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Seafood)
    if freshness:
        q = q.filter(Seafood.freshness_grade == freshness)
    if status:
        q = q.filter(Seafood.status == status)
    items = q.order_by(Seafood.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return [serialize(x) for x in items]

@router.get("/{seafood_id}")
def get_seafood(seafood_id: int, db: Session = Depends(get_db)):
    item = db.get(Seafood, seafood_id)
    if not item:
        raise HTTPException(404, "상품을 찾을 수 없습니다")
    return serialize(item)

@router.patch("/{seafood_id}/catch")
def update_catch(seafood_id: int, payload: CatchUpdate, db: Session = Depends(get_db)):
    item = db.get(Seafood, seafood_id)
    if not item:
        raise HTTPException(404, "상품을 찾을 수 없습니다")

    item.catch_amount = payload.catch_amount
    if payload.stock_quantity is not None:
        item.stock_quantity = payload.stock_quantity
        if item.stock_quantity == 0:
            item.status = "SOLD_OUT"

    db.commit()
    db.refresh(item)
    return serialize(item)

@router.patch("/{seafood_id}/freshness")
def update_freshness(seafood_id: int, payload: FreshnessUpdate, db: Session = Depends(get_db)):
    item = db.get(Seafood, seafood_id)
    if not item:
        raise HTTPException(404, "상품을 찾을 수 없습니다")

    item.freshness_grade = payload.freshness_grade.value
    if item.status not in ("SOLD_OUT", "CLOSED") and payload.freshness_grade.value == "C":
        item.status = "DISCOUNTED"

    db.commit()
    db.refresh(item)
    return serialize(item)

@router.post("/{seafood_id}/price-calculate")
def price_calculate(seafood_id: int, rules: PriceCalculateRequest, db: Session = Depends(get_db)):
    item = db.get(Seafood, seafood_id)
    if not item:
        raise HTTPException(404, "상품을 찾을 수 없습니다")

    final_price, adjustments = calculate_price(item, rules)
    item.final_price = final_price

    # 종결 상태는 역행하지 않도록 유지.
    if item.status not in ("SOLD_OUT", "CLOSED"):
        if item.freshness_grade == "C" or item.stock_quantity > 50:
            item.status = "DISCOUNTED"
        else:
            item.status = "PRICE_UPDATED"

    history = PriceHistory(
        seafood_id=item.id,
        base_price=item.base_price,
        final_price=final_price,
        freshness_adjustment=adjustments.get("freshness"),
        catch_adjustment=adjustments.get("catch"),
        stock_adjustment=adjustments.get("stock"),
    )
    db.add(history)
    db.commit()

    return {
        "seafood_id": item.id,
        "base_price": item.base_price,
        "final_price": final_price,
        "adjustments": adjustments,
        "status": item.status,
    }
