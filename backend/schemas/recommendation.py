"""
Pydantic schemas for recommendation API responses
"""

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum


class RecommendationSignalEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TechnicalIndicatorsSchema(BaseModel):
    """Technical indicators for a stock"""
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    sma_10: Optional[float] = None
    sma_50: Optional[float] = None
    current_price: float


class RecommendationBase(BaseModel):
    """Base recommendation schema"""
    symbol: str
    signal: RecommendationSignalEnum
    confidence: float


class RecommendationResponse(RecommendationBase):
    """Response schema for a recommendation"""
    id: str
    user_id: str
    rsi_score: float
    macd_score: float
    sma_score: float
    indicators: TechnicalIndicatorsSchema
    updated_at: datetime

    class Config:
        from_attributes = True


class RecommendationHistoryResponse(BaseModel):
    """Response schema for recommendation history"""
    id: str
    symbol: str
    signal: RecommendationSignalEnum
    confidence: float
    price_at_recommendation: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class RecommendationSummaryResponse(BaseModel):
    """Summary of user recommendations"""
    total: int
    buy_count: int
    sell_count: int
    hold_count: int
    top_buy: List[RecommendationResponse]
    top_sell: List[RecommendationResponse]


class RecommendationUpdateRequest(BaseModel):
    """Request to update recommendations"""
    user_id: str
