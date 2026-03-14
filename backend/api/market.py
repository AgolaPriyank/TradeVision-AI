from fastapi import APIRouter, HTTPException
import yfinance as yf

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
