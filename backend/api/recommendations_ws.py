"""
Real-time recommendation WebSocket endpoint.

Provides streaming recommendation updates for user portfolios.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
import json
import asyncio
from typing import Dict, Set

from api.deps import get_current_user, get_db
from models.user import User
from services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/ws/recommendations", tags=["websockets"])


class RecommendationConnectionManager:
    """Manages WebSocket connections for real-time recommendations"""
    
    def __init__(self):
        # user_id -> set of active websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # background tasks by user_id
        self.tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection and start recommendation updates"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
            # Start background task for this user
            self.tasks[user_id] = asyncio.create_task(
                self.broadcast_recommendation_updates(user_id)
            )
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove connection and cleanup if no more connections for this user"""
        if user_id in self.active_connections and websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.tasks:
                    self.tasks[user_id].cancel()
                    del self.tasks[user_id]

    async def broadcast_recommendation_updates(self, user_id: str):
        """
        Periodically fetch and broadcast recommendation updates.
        
        Updates every 30 seconds to balance freshness with API rate limits.
        """
        try:
            from database.database import SessionLocal
            
            while True:
                if user_id not in self.active_connections or not self.active_connections[user_id]:
                    break

                db = SessionLocal()
                try:
                    # Get updated recommendations
                    RecommendationEngine.update_user_recommendations(db, user_id)
                    recommendations = RecommendationEngine.get_user_recommendations(db, user_id)
                    summary = RecommendationEngine.get_signal_summary(db, user_id)

                    message = {
                        "type": "recommendations_update",
                        "user_id": user_id,
                        "summary": {
                            "total": summary['total'],
                            "buy_count": summary['buy_count'],
                            "sell_count": summary['sell_count'],
                            "hold_count": summary['hold_count'],
                        },
                        "recommendations": [
                            {
                                "symbol": r.symbol,
                                "signal": r.signal.value,
                                "confidence": float(r.confidence),
                                "current_price": float(r.current_price) if r.current_price else None,
                                "rsi_14": float(r.rsi_14) if r.rsi_14 else None,
                                "macd": float(r.macd) if r.macd else None,
                                "updated_at": r.updated_at.isoformat(),
                            }
                            for r in recommendations
                        ]
                    }

                    # Send to all connected clients for this user
                    websockets = list(self.active_connections.get(user_id, set()))
                    for connection in websockets:
                        try:
                            await connection.send_text(json.dumps(message))
                        except WebSocketDisconnect:
                            self.disconnect(connection, user_id)

                    # Update every 30 seconds
                    await asyncio.sleep(30)

                finally:
                    db.close()

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in recommendation broadcast for user {user_id}: {e}")


recommendation_manager = RecommendationConnectionManager()


@router.websocket("/portfolio")
async def websocket_recommendations(websocket: WebSocket):
    """
    WebSocket endpoint for real-time portfolio recommendations.
    
    Clients need to authenticate and will receive periodic updates
    on their stock recommendations.
    """
    # Note: WebSocket auth needs to be handled differently
    # This is a simplified version - in production, use token-based auth
    user_id = None
    
    try:
        await websocket.accept()
        
        # Wait for authentication message from client
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        
        if auth_data.get("type") == "auth":
            user_id = auth_data.get("user_id")
            
            if user_id:
                await recommendation_manager.connect(websocket, user_id)
                
                # Keep connection alive
                while True:
                    data = await websocket.receive_text()
                    client_message = json.loads(data)
                    
                    if client_message.get("type") == "refresh":
                        # Client requested immediate refresh
                        from database.database import SessionLocal
                        db = SessionLocal()
                        try:
                            RecommendationEngine.update_user_recommendations(db, user_id)
                            recommendations = RecommendationEngine.get_user_recommendations(db, user_id)
                            
                            message = {
                                "type": "recommendations_refresh",
                                "recommendations": [
                                    {
                                        "symbol": r.symbol,
                                        "signal": r.signal.value,
                                        "confidence": float(r.confidence),
                                    }
                                    for r in recommendations
                                ]
                            }
                            await websocket.send_text(json.dumps(message))
                        finally:
                            db.close()
            else:
                await websocket.close(code=1008, reason="Invalid user_id")
        else:
            await websocket.close(code=1008, reason="Authentication required")
            
    except WebSocketDisconnect:
        if user_id:
            recommendation_manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if user_id:
            recommendation_manager.disconnect(websocket, user_id)
