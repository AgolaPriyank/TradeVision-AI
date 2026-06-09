"""
Recommendation engine for generating stock recommendations based on technical analysis.
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime

from models.recommendation import Recommendation, RecommendationHistory, RecommendationSignal
from models.portfolio import Holding
from models.user import User
from services.technical_analysis import TechnicalAnalysisService


class RecommendationEngine:
    """Generates and manages stock recommendations"""

    @staticmethod
    def generate_recommendation_for_symbol(symbol: str) -> Optional[Dict]:
        """
        Generate a recommendation for a specific symbol.
        
        Returns:
            Dictionary with recommendation data or None if fails
        """
        try:
            indicators = TechnicalAnalysisService.calculate_indicators(symbol)
            if indicators is None:
                return None

            # Calculate individual scores
            rsi_score = TechnicalAnalysisService.calculate_rsi_score(indicators.get('rsi_14'))
            macd_score = TechnicalAnalysisService.calculate_macd_score(
                indicators.get('macd'),
                indicators.get('macd_signal'),
                indicators.get('macd_histogram')
            )
            sma_score = TechnicalAnalysisService.calculate_sma_score(
                indicators.get('current_price', 0),
                indicators.get('sma_10'),
                indicators.get('sma_50'),
                indicators.get('sma_10_above_sma_50', False)
            )

            # Calculate composite score (weighted average)
            # Equal weights for all three indicators
            composite_score = (rsi_score + macd_score + sma_score) / 3

            # Convert score to signal
            signal, confidence = TechnicalAnalysisService.score_to_signal(composite_score)

            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'composite_score': composite_score,
                'rsi_score': rsi_score,
                'macd_score': macd_score,
                'sma_score': sma_score,
                'indicators': indicators,
            }

        except Exception as e:
            print(f"Error generating recommendation for {symbol}: {e}")
            return None

    @staticmethod
    def update_user_recommendations(db: Session, user_id: str) -> List[Dict]:
        """
        Update recommendations for all stocks in a user's portfolio.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of updated recommendations
        """
        try:
            # Get user's portfolio holdings
            holdings = db.query(Holding).filter(
                Holding.portfolio_id == (
                    db.query(User).filter(User.id == user_id).first().id
                    if db.query(User).filter(User.id == user_id).first() else None
                )
            ).all()

            if not holdings:
                return []

            updated_recommendations = []

            for holding in holdings:
                if holding.shares > 0:  # Only recommend for holdings with shares
                    rec_data = RecommendationEngine.generate_recommendation_for_symbol(holding.symbol)
                    if rec_data:
                        # Update or create recommendation
                        rec = db.query(Recommendation).filter(
                            (Recommendation.user_id == user_id) &
                            (Recommendation.symbol == holding.symbol)
                        ).first()

                        if rec is None:
                            rec = Recommendation(
                                user_id=user_id,
                                symbol=holding.symbol
                            )
                            db.add(rec)

                        # Update recommendation fields
                        rec.signal = RecommendationSignal[rec_data['signal']]
                        rec.confidence = rec_data['confidence']
                        rec.rsi_14 = rec_data['indicators'].get('rsi_14')
                        rec.macd = rec_data['indicators'].get('macd')
                        rec.macd_signal = rec_data['indicators'].get('macd_signal')
                        rec.sma_10 = rec_data['indicators'].get('sma_10')
                        rec.sma_50 = rec_data['indicators'].get('sma_50')
                        rec.current_price = rec_data['indicators'].get('current_price')
                        rec.rsi_score = rec_data['rsi_score']
                        rec.macd_score = rec_data['macd_score']
                        rec.sma_score = rec_data['sma_score']
                        rec.updated_at = datetime.utcnow()

                        # Add to history
                        history = RecommendationHistory(
                            user_id=user_id,
                            symbol=holding.symbol,
                            signal=rec.signal,
                            confidence=rec.confidence,
                            price_at_recommendation=rec.current_price,
                            rsi_14=rec.rsi_14,
                            macd=rec.macd,
                            sma_10=rec.sma_10,
                            sma_50=rec.sma_50,
                        )
                        db.add(history)

                        updated_recommendations.append(rec_data)

            db.commit()
            return updated_recommendations

        except Exception as e:
            db.rollback()
            print(f"Error updating recommendations for user {user_id}: {e}")
            return []

    @staticmethod
    def get_user_recommendations(db: Session, user_id: str) -> List[Recommendation]:
        """
        Get all current recommendations for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of Recommendation objects
        """
        return db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).order_by(Recommendation.signal).all()

    @staticmethod
    def get_recommendation_history(
        db: Session,
        user_id: str,
        symbol: str,
        limit: int = 50
    ) -> List[RecommendationHistory]:
        """
        Get recommendation history for a specific holding.
        
        Args:
            db: Database session
            user_id: User ID
            symbol: Stock ticker symbol
            limit: Number of records to return
            
        Returns:
            List of RecommendationHistory objects
        """
        return db.query(RecommendationHistory).filter(
            (RecommendationHistory.user_id == user_id) &
            (RecommendationHistory.symbol == symbol)
        ).order_by(RecommendationHistory.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_signal_summary(db: Session, user_id: str) -> Dict:
        """
        Get a summary of all signals for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with signal counts and top recommendations
        """
        recommendations = RecommendationEngine.get_user_recommendations(db, user_id)
        
        summary = {
            'total': len(recommendations),
            'buy_count': sum(1 for r in recommendations if r.signal == RecommendationSignal.BUY),
            'sell_count': sum(1 for r in recommendations if r.signal == RecommendationSignal.SELL),
            'hold_count': sum(1 for r in recommendations if r.signal == RecommendationSignal.HOLD),
            'top_buy': sorted(
                [r for r in recommendations if r.signal == RecommendationSignal.BUY],
                key=lambda x: x.confidence,
                reverse=True
            )[:5],
            'top_sell': sorted(
                [r for r in recommendations if r.signal == RecommendationSignal.SELL],
                key=lambda x: x.confidence,
                reverse=True
            )[:5],
        }
        
        return summary
