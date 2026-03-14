from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
import yfinance as yf
from database.database import get_db
from models.order import Order, OrderSide, OrderType, OrderStatus
from models.portfolio import Portfolio, Holding
from models.user import User
from schemas.order import OrderCreate, OrderResponse
from api.deps import get_current_user

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

def get_live_price(symbol: str) -> Decimal:
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.last_price
        if price is None:
            raise ValueError(f"Could not fetch price for {symbol}")
        return Decimal(str(price))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Market data unavailable: {e}")

@router.post("/", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Ensure user has a portfolio
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id)
        db.add(portfolio)
        db.commit()
    
    # 2. Simulate Order Matching (For MARKET orders we execute instantly)
    executed_price = None
    status = OrderStatus.PENDING

    if order.order_type == OrderType.MARKET:
        live_price = get_live_price(order.symbol)
        total_cost = live_price * order.quantity
        
        if order.order_side == OrderSide.BUY:
            if portfolio.available_balance < total_cost:
                raise HTTPException(status_code=400, detail="Insufficient funds")
            
            # Deduct balance
            portfolio.available_balance -= total_cost
            portfolio.total_invested += total_cost
            
            # Update holdings
            holding = db.query(Holding).filter(Holding.portfolio_id == portfolio.id, Holding.symbol == order.symbol).first()
            if holding:
                # Update average buy price
                total_value = (holding.shares * holding.avg_buy_price) + total_cost
                holding.shares += order.quantity
                holding.avg_buy_price = total_value / holding.shares
            else:
                holding = Holding(portfolio_id=portfolio.id, symbol=order.symbol, shares=order.quantity, avg_buy_price=live_price)
                db.add(holding)
                
            executed_price = live_price
            status = OrderStatus.EXECUTED

        elif order.order_side == OrderSide.SELL:
            holding = db.query(Holding).filter(Holding.portfolio_id == portfolio.id, Holding.symbol == order.symbol).first()
            if not holding or holding.shares < order.quantity:
                raise HTTPException(status_code=400, detail="Insufficient shares")
            
            # Add balance
            portfolio.available_balance += total_cost
            portfolio.total_invested -= (holding.avg_buy_price * order.quantity) # Approximate removal
            
            # Update holdings
            holding.shares -= order.quantity
            if holding.shares == 0:
                db.delete(holding)
                
            executed_price = live_price
            status = OrderStatus.EXECUTED

    # 3. Create Order Record
    new_order = Order(
        user_id=current_user.id,
        symbol=order.symbol,
        order_side=order.order_side.value,
        order_type=order.order_type.value,
        quantity=order.quantity,
        limit_price=order.limit_price,
        status=status.value,
        executed_price=executed_price
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
