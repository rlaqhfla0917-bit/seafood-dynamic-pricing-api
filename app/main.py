from fastapi import FastAPI

from .database import Base, engine
from .routes import orders, seafoods

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Seafood Dynamic Pricing API",
    version="1.0.0",
    description="신선도·어획량·재고량 기반 수산물 가격 자동 조정 및 주문 관리 API",
)

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}

app.include_router(seafoods.router)
app.include_router(orders.router)
