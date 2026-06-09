from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Index
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from database.database import Base


class RecommendationSignal(PyEnum):
    """Enum for recommendation signals"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Recommendation(Base):
    """
    Stores current recommendations for user holdings based on technical indicators.
    Each record represents the latest recommendation for a stock in a user's portfolio.
    """
    __tablename__ = "recommendations"
    __table_args__ = (
        Index('idx_user_symbol', 'user_id', 'symbol'),
        Index('idx_updated_at', 'updated_at'),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    symbol = Column(String, index=True)  # Stock ticker symbol
    
    # Recommendation signal
    signal = Column(Enum(RecommendationSignal), default=RecommendationSignal.HOLD)
    confidence = Column(Float, default=0.5)  # 0.0 to 1.0
    
    # Technical indicators used for recommendation
    rsi_14 = Column(Float, nullable=True)  # Relative Strength Index
    macd = Column(Float, nullable=True)  # MACD value
    macd_signal = Column(Float, nullable=True)  # MACD Signal line
    sma_10 = Column(Float, nullable=True)  # 10-day Simple Moving Average
    sma_50 = Column(Float, nullable=True)  # 50-day Simple Moving Average
    current_price = Column(Float, nullable=True)  # Current stock price
    
    # Reasoning and score breakdown
    rsi_score = Column(Float, default=0.0)  # 0.0 to 1.0
    macd_score = Column(Float, default=0.0)  # 0.0 to 1.0
    sma_score = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecommendationHistory(Base):
    """
    Tracks historical recommendations to show recommendation changes and trends.
    Useful for backtesting and analysis.
    """
    __tablename__ = "recommendation_history"
    __table_args__ = (
        Index('idx_user_symbol_timestamp', 'user_id', 'symbol', 'timestamp'),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    symbol = Column(String, index=True)
    
    signal = Column(Enum(RecommendationSignal))
    confidence = Column(Float)
    price_at_recommendation = Column(Float)
    
    rsi_14 = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    sma_10 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
