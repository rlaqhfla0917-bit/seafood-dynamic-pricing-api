from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Category(str, Enum):
    FISH = "FISH"
    SHELLFISH = "SHELLFISH"
    CRUSTACEAN = "CRUSTACEAN"
    OTHER = "OTHER"

class FreshnessGrade(str, Enum):
    A = "A"
    B = "B"
    C = "C"

class ProductStatus(str, Enum):
    DRAFT = "DRAFT"
    ON_SALE = "ON_SALE"
    PRICE_UPDATED = "PRICE_UPDATED"
    DISCOUNTED = "DISCOUNTED"
    SOLD_OUT = "SOLD_OUT"
    CLOSED = "CLOSED"

class OrderStatus(str, Enum):
    ORDERED = "ORDERED"
    PAID = "PAID"
    PACKING = "PACKING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"

class SeafoodCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: Category
    origin: Optional[str] = None
    base_price: int = Field(gt=0)
    unit: str = "kg"
    stock_quantity: int = Field(ge=0)
    freshness_grade: FreshnessGrade = FreshnessGrade.B
    catch_amount: int = Field(ge=0)
    status: ProductStatus = ProductStatus.ON_SALE

class CatchUpdate(BaseModel):
    catch_amount: int = Field(ge=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)

class FreshnessUpdate(BaseModel):
    freshness_grade: FreshnessGrade

class PriceCalculateRequest(BaseModel):
    apply_freshness_rule: bool = True
    apply_catch_rule: bool = True
    apply_stock_rule: bool = True
    apply_deadline_discount: bool = False

class OrderCreate(BaseModel):
    seafood_id: int
    quantity: int = Field(gt=0)

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
