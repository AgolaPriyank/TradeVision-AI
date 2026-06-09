"""
Recommendation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.user import User
from schemas.recommendation import (
    RecommendationResponse,
    RecommendationHistoryResponse,
    RecommendationSummaryResponse,
)
from services.recommendation_engine import RecommendationEngine

router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["recommendations"],
)


@router.get("/", response_model=list[RecommendationResponse])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all recommendations for the current user.
    
    Returns recommendations for all stocks currently held in the user's portfolio.
    """
    recommendations = RecommendationEngine.get_user_recommendations(db, current_user.id)
    
    if not recommendations:
        return []
    
    return recommendations


@router.get("/summary", response_model=RecommendationSummaryResponse)
def get_recommendation_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a summary of all recommendations for the current user.
    
    Returns counts of buy/sell/hold signals and top recommendations.
    """
    summary = RecommendationEngine.get_signal_summary(db, current_user.id)
    
    return RecommendationSummaryResponse(**summary)


@router.get("/symbol/{symbol}", response_model=RecommendationResponse)
def get_recommendation_for_symbol(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the recommendation for a specific symbol in the user's portfolio.
    """
    from models.recommendation import Recommendation
    
    recommendation = db.query(Recommendation).filter(
        (Recommendation.user_id == current_user.id) &
        (Recommendation.symbol == symbol.upper())
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendation found for {symbol}"
        )
    
    return recommendation


@router.get("/symbol/{symbol}/history", response_model=list[RecommendationHistoryResponse])
def get_recommendation_history(
    symbol: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get historical recommendations for a specific symbol.
    
    Useful for analyzing how recommendations have changed over time.
    
    Args:
        symbol: Stock ticker symbol
        limit: Number of historical records to return (default: 50, max: 500)
    """
    history = RecommendationEngine.get_recommendation_history(
        db,
        current_user.id,
        symbol.upper(),
        limit=limit
    )
    
    return history


@router.post("/refresh")
def refresh_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Refresh recommendations for all of the user's holdings.
    
    This recalculates all technical indicators and updates recommendations.
    """
    try:
        updated_recs = RecommendationEngine.update_user_recommendations(db, current_user.id)
        
        return {
            "status": "success",
            "message": f"Updated {len(updated_recs)} recommendations",
            "updated_count": len(updated_recs),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating recommendations: {str(e)}"
        )


@router.get("/buy-signals", response_model=list[RecommendationResponse])
def get_buy_signals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all stocks with BUY signals, sorted by confidence.
    """
    from models.recommendation import Recommendation, RecommendationSignal
    
    recommendations = db.query(Recommendation).filter(
        (Recommendation.user_id == current_user.id) &
        (Recommendation.signal == RecommendationSignal.BUY)
    ).order_by(Recommendation.confidence.desc()).all()
    
    return recommendations


@router.get("/sell-signals", response_model=list[RecommendationResponse])
def get_sell_signals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all stocks with SELL signals, sorted by confidence.
    """
    from models.recommendation import Recommendation, RecommendationSignal
    
    recommendations = db.query(Recommendation).filter(
        (Recommendation.user_id == current_user.id) &
        (Recommendation.signal == RecommendationSignal.SELL)
    ).order_by(Recommendation.confidence.desc()).all()
    
    return recommendations
