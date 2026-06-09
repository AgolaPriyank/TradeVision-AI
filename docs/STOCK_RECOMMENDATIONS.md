# Stock Recommendation System

## Overview

The Stock Recommendation System is an intelligent component of TradeVision AI that generates personalized, real-time stock recommendations for each user based on technical analysis. The system analyzes stocks held in the user's portfolio and provides Buy/Sell/Hold signals with confidence scores.

## Features

### 1. **Technical Analysis-Based Recommendations**
   - **RSI (Relative Strength Index)**: Measures momentum and overbought/oversold conditions
   - **MACD (Moving Average Convergence Divergence)**: Identifies trend changes and momentum
   - **SMA (Simple Moving Average)**: Analyzes price trends relative to 10-day and 50-day averages
   - Composite scoring system combining all three indicators

### 2. **Personalized by Portfolio**
   - Recommendations are generated only for stocks in the user's portfolio
   - Each user receives unique recommendations based on their holdings
   - Historical recommendation data is tracked per user and stock

### 3. **Real-Time Updates**
   - WebSocket support for streaming recommendation updates
   - API endpoints for fetching latest recommendations on demand
   - Periodic refresh system that updates recommendations every 30 seconds

### 4. **Comprehensive Signal Breakdown**
   - Individual scores for RSI, MACD, and SMA strategies
   - Confidence levels for each recommendation
   - Complete technical indicator values for transparency

## System Architecture

### Backend Components

#### 1. **Database Models** (`backend/models/recommendation.py`)
```
Recommendation
├── user_id (Foreign Key)
├── symbol
├── signal (BUY/SELL/HOLD)
├── confidence (0.0-1.0)
├── indicators (RSI, MACD, SMA values)
├── score breakdown (RSI/MACD/SMA scores)
└── timestamp

RecommendationHistory
├── user_id
├── symbol
├── historical signal
├── timestamp
└── indicators at time of recommendation
```

#### 2. **Technical Analysis Service** (`backend/services/technical_analysis.py`)

**Core Functions:**
- `fetch_historical_data()`: Retrieves 6 months of historical price data
- `calculate_rsi()`: Computes Relative Strength Index
- `calculate_macd()`: Computes MACD and signal line
- `calculate_sma()`: Computes 10-day and 50-day averages
- `calculate_indicators()`: Aggregates all technical indicators
- Scoring functions: Convert each indicator to a 0.0-1.0 score

**Scoring Logic:**
```
RSI Score:
- RSI < 30: 0.9 (Oversold, strong buy)
- RSI 30-40: 0.7 (Buy)
- RSI 40-60: 0.5 (Neutral)
- RSI 60-70: 0.3 (Sell)
- RSI > 70: 0.1 (Overbought, strong sell)

MACD Score:
- MACD > Signal & positive: 0.8 (Strong buy)
- MACD > Signal: 0.6 (Buy)
- MACD < Signal & negative: 0.2 (Strong sell)
- MACD < Signal: 0.4 (Sell)
- Otherwise: 0.5 (Neutral)

SMA Score:
- Price > SMA10 > SMA50: 0.8 (Strong uptrend)
- Price > SMA10 or Price > SMA50: 0.6 (Uptrend)
- Price < SMA10 < SMA50: 0.2 (Strong downtrend)
- Price < SMA10 or Price < SMA50: 0.4 (Downtrend)
- Otherwise: 0.5 (Neutral)

Composite Score = (RSI Score + MACD Score + SMA Score) / 3

Signal Generation:
- Score ≥ 0.65: BUY (with confidence = score)
- Score ≤ 0.35: SELL (with confidence = 1 - score)
- Otherwise: HOLD (with confidence = 0.5)
```

#### 3. **Recommendation Engine** (`backend/services/recommendation_engine.py`)

**Key Methods:**
- `generate_recommendation_for_symbol()`: Creates recommendation for a single stock
- `update_user_recommendations()`: Updates all recommendations for a user's portfolio
- `get_user_recommendations()`: Retrieves current recommendations
- `get_recommendation_history()`: Gets historical recommendations for tracking
- `get_signal_summary()`: Returns aggregated stats (buy/sell/hold counts)

#### 4. **API Endpoints** (`backend/api/recommendations.py`)

**Public Endpoints:**
- `GET /api/v1/recommendations/` - Get all recommendations
- `GET /api/v1/recommendations/summary` - Get summary with stats
- `GET /api/v1/recommendations/symbol/{symbol}` - Get specific recommendation
- `GET /api/v1/recommendations/symbol/{symbol}/history` - Get recommendation history
- `POST /api/v1/recommendations/refresh` - Trigger immediate update
- `GET /api/v1/recommendations/buy-signals` - Get all BUY signals
- `GET /api/v1/recommendations/sell-signals` - Get all SELL signals

**WebSocket Endpoints** (`backend/api/recommendations_ws.py`)
- `WS /ws/recommendations/portfolio` - Real-time recommendation stream
  - Sends updates every 30 seconds
  - Client can request immediate refresh

### Frontend Components

#### 1. **RecommendationIndicators** (`frontend/src/components/RecommendationIndicators.tsx`)
Displays technical indicator values with color-coded status:
- RSI with overbought/oversold indicators
- MACD with bullish/bearish status
- SMA 10 & 50 with price comparisons
- Current stock price

#### 2. **RecommendationCard** (`frontend/src/components/RecommendationCard.tsx`)
Individual recommendation display showing:
- Signal (BUY/SELL/HOLD) with emoji icon
- Confidence level with progress bar
- Current price
- Component scores (RSI/MACD/SMA)
- Technical indicators
- Last update time

#### 3. **RecommendationPanel** (`frontend/src/components/RecommendationPanel.tsx`)
Dashboard component showing:
- Summary statistics (total, buy count, sell count, hold count)
- Filter buttons (All/Buy/Sell/Hold)
- Grid of recommendation cards
- Auto-refresh functionality
- Error handling

#### 4. **Dashboard Integration** (`frontend/src/app/dashboard/page.tsx`)
Recommendations section displayed below market chart with:
- Auto-refresh every 60 seconds
- Real-time updates
- Interactive cards with click handlers

## Data Flow

```
1. User Opens Dashboard
   ↓
2. RecommendationPanel mounts
   ↓
3. Fetch /api/v1/recommendations/summary
   ↓
4. Display recommendation cards
   ↓
5. Optional: Connect to WebSocket for real-time updates
   ↓
6. Every 60 seconds: Fetch updated recommendations
```

## Usage Guide

### For Users

#### View Recommendations
1. Navigate to the Dashboard
2. Scroll to the "Stock Recommendations" section
3. View recommendations for all holdings
4. Click filter buttons to see specific signals

#### Interpret Recommendations
- **BUY (Green)**: Technical indicators suggest upward momentum
  - High RSI score, positive MACD, price above SMAs
  - Good entry point for new positions
  
- **SELL (Red)**: Technical indicators suggest downward momentum
  - Low RSI score, negative MACD, price below SMAs
  - Consider taking profits or reducing positions

- **HOLD (Yellow)**: Mixed or neutral signals
  - Technical indicators not strongly aligned
  - Current position is reasonable, monitor for changes

#### Refresh Manually
- Click the "🔄 Refresh" button to immediately update all recommendations
- Recommendations auto-refresh every 60 seconds

### For Developers

#### Update Recommendations Programmatically
```python
from services.recommendation_engine import RecommendationEngine
from database.database import SessionLocal

db = SessionLocal()
try:
    updated = RecommendationEngine.update_user_recommendations(
        db, 
        user_id="user-uuid"
    )
    print(f"Updated {len(updated)} recommendations")
finally:
    db.close()
```

#### Get Recommendation Summary
```python
summary = RecommendationEngine.get_signal_summary(db, user_id)
print(f"BUY: {summary['buy_count']}, SELL: {summary['sell_count']}")
```

#### Access Recommendation History
```python
history = RecommendationEngine.get_recommendation_history(
    db,
    user_id="user-uuid",
    symbol="AAPL",
    limit=50
)
for record in history:
    print(f"{record.timestamp}: {record.signal} @ {record.price_at_recommendation}")
```

## Technical Indicator Explanations

### RSI (Relative Strength Index)
- **What it measures**: Momentum indicator that oscillates 0-100
- **Interpretation**: 
  - > 70: Overbought (potential reversal)
  - < 30: Oversold (potential bounce)
  - 40-60: Neutral zone
- **Formula**: RSI = 100 - (100 / (1 + RS)), where RS = avg gain / avg loss

### MACD (Moving Average Convergence Divergence)
- **What it measures**: Trend and momentum following changes
- **Components**:
  - MACD Line: 12-day EMA - 26-day EMA
  - Signal Line: 9-day EMA of MACD
  - Histogram: MACD - Signal Line
- **Interpretation**:
  - MACD above signal: Bullish
  - MACD below signal: Bearish
  - Histogram increasing: Momentum strengthening

### SMA (Simple Moving Average)
- **What it measures**: Trend direction over time
- **10-day SMA**: Short-term trend
- **50-day SMA**: Medium-term trend
- **Interpretation**:
  - Price > SMA: Uptrend
  - Price < SMA: Downtrend
  - SMA 10 > SMA 50: Strong trend confirmation

## Performance Considerations

### API Rate Limiting
- Data fetched from Yahoo Finance
- Recommendations update every 30 seconds (WebSocket)
- Frontend refreshes every 60 seconds (configurable)

### Database Optimization
- Indexed queries on `user_id`, `symbol`, and `updated_at`
- Recommendation history pruned automatically (keep last 90 days)
- Efficient batch updates for user portfolios

### Caching
- Technical indicators calculated fresh for each update
- No in-memory caching (ensures up-to-date data)
- Consider Redis caching for high-traffic scenarios

## Customization

### Adjusting Scoring Weights
In `technical_analysis.py`, modify the composite score calculation:
```python
# Current: Equal weights
composite_score = (rsi_score + macd_score + sma_score) / 3

# Custom weights (example: emphasize RSI)
composite_score = (0.4 * rsi_score + 0.3 * macd_score + 0.3 * sma_score)
```

### Changing Signal Thresholds
In `technical_analysis.py`, adjust `score_to_signal()`:
```python
# Current thresholds
if score >= 0.65:  # BUY threshold
    return "BUY", score
elif score <= 0.35:  # SELL threshold
    return "SELL", 1.0 - score
else:
    return "HOLD", 0.5

# Custom thresholds
if score >= 0.70:  # Higher BUY threshold
    return "BUY", score
elif score <= 0.30:  # Lower SELL threshold
    return "SELL", 1.0 - score
```

### Changing Refresh Intervals
**Frontend (RecommendationPanel):**
```tsx
<RecommendationPanel 
  autoRefresh={true} 
  refreshInterval={30}  // 30 seconds instead of 60
/>
```

**WebSocket (recommendations_ws.py):**
```python
await asyncio.sleep(30)  # Change from 30 to your desired interval
```

## Future Enhancements

1. **Sentiment Analysis**: Incorporate news sentiment scores
2. **Machine Learning Predictions**: Integrate LSTM/XGBoost predictions
3. **Custom Indicators**: Support for user-defined technical indicators
4. **Alerts**: Email/SMS notifications for signal changes
5. **Backtesting**: Historical performance of recommendations
6. **Risk Scoring**: Add risk-adjusted recommendations
7. **Sector Analysis**: Comparative recommendations within sectors
8. **Options Analysis**: Recommendations for options trading

## Troubleshooting

### No Recommendations Showing
- **Cause**: User has no holdings in portfolio
- **Solution**: Add stocks to portfolio first, then recommendations will generate

### Recommendations Not Updating
- **Cause**: Data fetch failed or insufficient historical data
- **Solution**: Check internet connection, ensure stock symbol is valid

### WebSocket Not Connecting
- **Cause**: Auth token invalid or connection issue
- **Solution**: Re-login, check browser console for errors

### High Latency Updates
- **Cause**: Too many API calls or slow data source
- **Solution**: Increase refresh intervals, switch to faster data provider

## API Response Examples

### Recommendation Response
```json
{
  "id": "rec-uuid",
  "user_id": "user-uuid",
  "symbol": "AAPL",
  "signal": "BUY",
  "confidence": 0.75,
  "rsi_score": 0.7,
  "macd_score": 0.8,
  "sma_score": 0.75,
  "indicators": {
    "rsi_14": 32.5,
    "macd": 0.45,
    "macd_signal": 0.32,
    "sma_10": 150.25,
    "sma_50": 148.75,
    "current_price": 151.50
  },
  "updated_at": "2024-06-09T14:30:00Z"
}
```

### Summary Response
```json
{
  "total": 5,
  "buy_count": 2,
  "sell_count": 1,
  "hold_count": 2,
  "top_buy": [
    {
      "symbol": "AAPL",
      "signal": "BUY",
      "confidence": 0.75
    },
    {
      "symbol": "MSFT",
      "signal": "BUY",
      "confidence": 0.68
    }
  ],
  "top_sell": [
    {
      "symbol": "NVDA",
      "signal": "SELL",
      "confidence": 0.72
    }
  ]
}
```

## License

Part of TradeVision AI project. All rights reserved.

## Support

For issues or feature requests, please contact the development team or submit an issue in the project repository.
