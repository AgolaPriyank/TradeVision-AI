from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Enum as SQLEnum
import uuid
from datetime import datetime
from database.database import Base
import enum

class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    symbol = Column(String, index=True)
    order_side = Column(SQLEnum(OrderSide))
    order_type = Column(SQLEnum(OrderType))
    quantity = Column(Integer)
    limit_price = Column(Numeric, nullable=True) # Used for limit orders
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    executed_price = Column(Numeric, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
