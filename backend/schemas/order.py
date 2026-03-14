from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.order import OrderSide, OrderType, OrderStatus

class OrderCreate(BaseModel):
    symbol: str
    order_side: OrderSide
    order_type: OrderType
    quantity: int
    limit_price: Optional[float] = None

class OrderResponse(BaseModel):
    id: str
    symbol: str
    order_side: OrderSide
    order_type: OrderType
    quantity: int
    limit_price: Optional[float]
    status: OrderStatus
    executed_price: Optional[float]
    created_at: str

    class Config:
        from_attributes = True
