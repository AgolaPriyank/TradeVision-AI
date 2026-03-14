from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from models import user, order, portfolio

# Create tables (SQLite auto-creation for now)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TradeVision AI API",
    version="1.0.0",
    description="Backend API for the Stock Market Trading Web Platform"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.auth import router as auth_router
from api.market import router as market_router
from api.websockets import router as ws_router
from api.orders import router as orders_router
from api.portfolio import router as portfolio_router

app.include_router(auth_router)
app.include_router(market_router)
app.include_router(ws_router)
app.include_router(orders_router)
app.include_router(portfolio_router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "TradeVision AI API is running"}
