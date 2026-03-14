from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from models.portfolio import Portfolio, Holding
from models.user import User
from api.deps import get_current_user
import yfinance as yf
from decimal import Decimal

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])

@router.get("/")
def get_portfolio_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        portfolio = Portfolio(user_id=current_user.id)
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
    
    current_value = Decimal('0.0')
    holding_details = []
    
    for h in holdings:
        try:
             ticker = yf.Ticker(h.symbol)
             price = Decimal(str(ticker.fast_info.get('last_price', 0)))
        except:
             price = h.avg_buy_price
             
        value = price * h.shares
        current_value += value
        
        holding_details.append({
            "symbol": h.symbol,
            "shares": h.shares,
            "avg_buy_price": h.avg_buy_price,
            "current_price": price,
            "current_value": value,
            "pnl": value - (h.avg_buy_price * h.shares),
            "pnl_percentage": ((price - h.avg_buy_price) / h.avg_buy_price * 100) if h.avg_buy_price > 0 else 0
        })

    return {
        "available_balance": portfolio.available_balance,
        "total_invested": portfolio.total_invested,
        "current_value": current_value,
        "total_pnl": current_value - portfolio.total_invested,
        "holdings": holding_details
    }
