from fastapi import FastAPI, HTTPException
import joblib
import os
import yfinance as yf
import pandas as pd
import sys

# Ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from feature_engineering.indicators import engineer_features

app = FastAPI(title="TradeVision AI - ML Predictor API")

def load_model(symbol: str):
    model_path = f"../models_store/{symbol}_xgboost.pkl"
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

@app.get("/api/v1/ml/predict/{symbol}")
def predict_trend(symbol: str):
    model = load_model(symbol)
    if not model:
        raise HTTPException(status_code=404, detail=f"No trained model found for {symbol}")
        
    try:
        # Fetch last 100 days to calculate features properly (requires 50 days for SMA_50)
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="100d")
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Failed to fetch recent data")
            
        df = engineer_features(df)
        
        # We only need the very last row for tomorrow's prediction
        latest_features = df.iloc[-1:]
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_10', 'SMA_50', 'RSI_14', 'MACD', 'MACD_Signal']
        X = latest_features[features]
        
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0].max()
        
        recommendation = "BUY" if prediction == 1 else "SELL"
        if probability < 0.55: # Low confidence
            recommendation = "HOLD"
            
        return {
            "symbol": symbol,
            "prediction": int(prediction),
            "recommendation": recommendation,
            "confidence": float(probability),
            "latest_close": float(latest_features['Close'].iloc[0])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/health")
def health_check():
    return {"status": "ok"}
