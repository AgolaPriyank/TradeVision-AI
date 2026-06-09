from fastapi import APIRouter, HTTPException
import yfinance as yf
import pandas as pd

router = APIRouter(prefix="/api/v1/market", tags=["market"])

@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "price": info.get("currentPrice", info.get("regularMarketPrice")),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "volume": info.get("volume")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch market data: {str(e)}")

@router.get("/history/{symbol}")
def get_history(symbol: str, range: str = "1mo", interval: str = "1d"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=range, interval=interval)
        if hist.empty:
            raise ValueError("No data found")
        
        hist = hist.reset_index()
        # Ensure 'Date' or 'Datetime' column is formatted
        date_col = 'Date' if 'Date' in hist.columns else 'Datetime'
        hist[date_col] = hist[date_col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        records = hist.to_dict('records')
        return {"symbol": symbol, "history": records}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch historical data: {str(e)}")


def calculate_rsi(data, window: int = 14, column: str = 'Close'):
    delta = data[column].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


@router.get("/recommend/{symbol}")
def get_recommendation(symbol: str, period: str = "3mo", interval: str = "1d"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        if hist.empty:
            raise ValueError("No historical data available")

        df = hist.copy()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI_14'] = calculate_rsi(df, 14)

        latest = df.iloc[-1]
        close_price = latest['Close']
        sma_10 = latest['SMA_10']
        sma_50 = latest['SMA_50']
        rsi_14 = latest['RSI_14']

        if pd.isna(sma_10) or pd.isna(sma_50) or pd.isna(rsi_14):
            raise ValueError("Not enough data to compute recommendation signals")

        recommendation = "HOLD"
        if close_price > sma_10 and close_price > sma_50 and rsi_14 < 70:
            recommendation = "BUY"
        elif close_price < sma_10 and close_price < sma_50 and rsi_14 > 55:
            recommendation = "SELL"

        return {
            "symbol": symbol,
            "recommendation": recommendation,
            "latest_close": float(close_price),
            "sma_10": float(sma_10),
            "sma_50": float(sma_50),
            "rsi_14": float(rsi_14),
            "period": period,
            "interval": interval
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate recommendation: {str(e)}")
