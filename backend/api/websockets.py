from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import yfinance as yf
from typing import Dict, Set

router = APIRouter(prefix="/ws", tags=["websockets"])

class ConnectionManager:
    def __init__(self):
        # symbol -> set of active websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # background tasks
        self.tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, symbol: str):
        await websocket.accept()
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
            # Start background task to fetch price if not exists
            self.tasks[symbol] = asyncio.create_task(self.broadcast_price_updates(symbol))
        self.active_connections[symbol].add(websocket)

    def disconnect(self, websocket: WebSocket, symbol: str):
        if symbol in self.active_connections and websocket in self.active_connections[symbol]:
            self.active_connections[symbol].remove(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
                if symbol in self.tasks:
                    self.tasks[symbol].cancel()
                    del self.tasks[symbol]

    async def broadcast_price_updates(self, symbol: str):
        try:
            while True:
                if symbol not in self.active_connections or not self.active_connections[symbol]:
                    break
                
                # Fetch live price
                # For a production app this should be replaced with a proper websocket feed from a market provider (e.g. Polygon.io websocket)
                # Since yfinance is a REST abstraction, we'll poll it for demonstration purposes every a few seconds.
                ticker = yf.Ticker(symbol)
                info = ticker.fast_info
                
                price = info.get('last_price', None)
                
                if price is not None:
                    message = json.dumps({
                        "type": "trade",
                        "symbol": symbol,
                        "price": price,
                        "timestamp": asyncio.get_event_loop().time()
                    })
                    
                    # Create a copy of the set before iterating to avoid 'Set changed size during iteration'
                    websockets = list(self.active_connections.get(symbol, set()))
                    for connection in websockets:
                        try:
                            await connection.send_text(message)
                        except WebSocketDisconnect:
                            self.disconnect(connection, symbol)
                
                await asyncio.sleep(5)  # Poll every 5 seconds to avoid rate matching limit from YF
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error in broadcast loop for {symbol}: {e}")


manager = ConnectionManager()

@router.websocket("/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await manager.connect(websocket, symbol)
    try:
        while True:
            # We expect the client to keep the connection alive but we mainly push data to them
            data = await websocket.receive_text()
            # Handle client messages if any (e.g. ping/pong or subscribe to more symbols)
    except WebSocketDisconnect:
        manager.disconnect(websocket, symbol)
