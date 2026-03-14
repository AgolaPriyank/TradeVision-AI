from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
import uuid
from database.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    available_balance = Column(Numeric, default=100000.00) # Give new users 100k paper money
    total_invested = Column(Numeric, default=0.00)

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"))
    symbol = Column(String, index=True)
    shares = Column(Integer, default=0)
    avg_buy_price = Column(Numeric, default=0.00)
