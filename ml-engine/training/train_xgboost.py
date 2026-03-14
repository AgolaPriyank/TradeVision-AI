import yfinance as yf
import pandas as pd
import os
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import sys

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from feature_engineering.indicators import engineer_features

def fetch_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    print(f"Fetching data for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end)
    return df

def train_model(symbol: str):
    df = fetch_data(symbol, start="2020-01-01", end="2024-01-01")
    if df.empty:
        print(f"No data for {symbol}")
        return
        
    df = engineer_features(df)
    
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_10', 'SMA_50', 'RSI_14', 'MACD', 'MACD_Signal']
    X = df[features]
    y = df['Target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )
    
    print(f"Training XGBoost model for {symbol}...")
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy for {symbol}: {accuracy:.2f}")
    
    # Ensure models directory exists
    os.makedirs('../models_store', exist_ok=True)
    
    model_path = f"../models_store/{symbol}_xgboost.pkl"
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    test_symbols = ['AAPL', 'MSFT', 'TSLA']
    for sym in test_symbols:
        train_model(sym)
