from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .database import Base

class Seafood(Base):
    __tablename__ = "seafoods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)
    origin = Column(String(100), nullable=True)
    base_price = Column(Integer, nullable=False)
    final_price = Column(Integer, nullable=True)
    unit = Column(String(20), nullable=False, default="kg")
    stock_quantity = Column(Integer, nullable=False, default=0)
    freshness_grade = Column(String(2), nullable=False, default="B")
    catch_amount = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="ON_SALE")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    orders = relationship("Order", back_populates="seafood")
    price_history = relationship("PriceHistory", back_populates="seafood")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    seafood_id = Column(Integer, ForeignKey("seafoods.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="ORDERED")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    seafood = relationship("Seafood", back_populates="orders")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    seafood_id = Column(Integer, ForeignKey("seafoods.id"), nullable=False)
    base_price = Column(Integer, nullable=False)
    final_price = Column(Integer, nullable=False)
    freshness_adjustment = Column(String(20), nullable=True)
    catch_adjustment = Column(String(20), nullable=True)
    stock_adjustment = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    seafood = relationship("Seafood", back_populates="price_history")
