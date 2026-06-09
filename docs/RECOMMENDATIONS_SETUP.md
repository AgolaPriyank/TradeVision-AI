# Stock Recommendation System - Quick Start Guide

## Installation

### 1. Backend Dependencies

The stock recommendation system requires the following Python packages (already in `requirements.txt`):
- `yfinance>=0.2.28` - For fetching historical stock data
- `pandas` - For data manipulation
- `numpy` - For numerical calculations

Verify these are installed:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Database Migration

The recommendation tables will be created automatically when the backend starts:
```bash
python main.py
```

This will create:
- `recommendations` table
- `recommendation_history` table

### 3. Frontend Setup

No additional dependencies needed. The components use existing Tailwind CSS styling.

## Running the System

### Start Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```

The recommendation system will:
1. ✅ Load on dashboard automatically
2. ✅ Fetch recommendations for user holdings
3. ✅ Auto-refresh every 60 seconds
4. ✅ Display BUY/SELL/HOLD signals

## First Test

1. **Login** to the application
2. **Add stocks** to your portfolio (if you haven't already)
3. **Go to Dashboard** - scroll to "Stock Recommendations" section
4. **View recommendations** for your holdings
5. **Click Refresh** button to manually trigger updates

## Example API Calls

### Get All Recommendations
```bash
curl -X GET http://localhost:8000/api/v1/recommendations/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Recommendations Summary
```bash
curl -X GET http://localhost:8000/api/v1/recommendations/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get BUY Signals
```bash
curl -X GET http://localhost:8000/api/v1/recommendations/buy-signals \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Manually Refresh Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/recommendations/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Recommendation History for a Stock
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/symbol/AAPL/history?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## WebSocket Connection

For real-time recommendations (advanced):

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/recommendations/portfolio');

ws.onopen = () => {
  // Send auth message
  ws.send(JSON.stringify({
    type: 'auth',
    user_id: 'your-user-id'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Recommendations updated:', data);
  
  // Request immediate refresh
  ws.send(JSON.stringify({
    type: 'refresh'
  }));
};
```

## Configuration

### Change Refresh Interval (Frontend)

In `frontend/src/app/dashboard/page.tsx`:
```tsx
<RecommendationPanel 
  autoRefresh={true} 
  refreshInterval={30}  // Update every 30 seconds instead of 60
/>
```

### Change Recommendation Thresholds

In `backend/services/technical_analysis.py`, modify `score_to_signal()`:
```python
@staticmethod
def score_to_signal(score: float) -> Tuple[str, float]:
    if score >= 0.70:  # More conservative BUY threshold
        return "BUY", min(score, 1.0)
    elif score <= 0.30:  # More conservative SELL threshold
        return "SELL", 1.0 - min(score, 1.0)
    else:
        return "HOLD", 0.5
```

### Change Scoring Weights

In `backend/services/recommendation_engine.py`, modify `generate_recommendation_for_symbol()`:
```python
# Give more weight to RSI
composite_score = (0.5 * rsi_score + 0.25 * macd_score + 0.25 * sma_score)
```

## Troubleshooting

### "No recommendations available"
- ✅ Make sure you have stocks in your portfolio
- ✅ Wait 30 seconds for recommendations to generate
- ✅ Try clicking "Refresh" button

### "Failed to fetch recommendations"
- ✅ Check authentication token is valid
- ✅ Make sure backend is running
- ✅ Check browser console for specific error

### "yfinance rate limit" errors
- ✅ Wait a few minutes before refreshing
- ✅ Consider upgrading to a paid data source
- ✅ Increase the refresh interval

### Stock data not available
- ✅ Verify stock symbol is correct
- ✅ Some stocks may not have 6 months of data
- ✅ Try a different stock symbol

## Next Steps

1. **Add more indicators** - Expand technical analysis
2. **Implement alerts** - Get notified of signal changes
3. **Backtesting** - Analyze historical recommendation accuracy
4. **Machine Learning** - Combine with predictive models
5. **Risk Scoring** - Add risk-adjusted recommendations

## File Structure

```
backend/
├── api/
│   ├── recommendations.py      # REST API endpoints
│   └── recommendations_ws.py   # WebSocket endpoints
├── services/
│   ├── technical_analysis.py   # Indicator calculations
│   └── recommendation_engine.py # Recommendation logic
├── models/
│   └── recommendation.py       # Database models
└── schemas/
    └── recommendation.py       # API response schemas

frontend/
├── src/
│   ├── app/
│   │   └── dashboard/page.tsx  # Dashboard with recommendations
│   └── components/
│       ├── RecommendationPanel.tsx       # Main panel component
│       ├── RecommendationCard.tsx        # Individual cards
│       └── RecommendationIndicators.tsx  # Indicator display
```

## Support

For detailed documentation, see [STOCK_RECOMMENDATIONS.md](STOCK_RECOMMENDATIONS.md)

For issues, check:
1. Backend logs
2. Browser developer console
3. Network tab in DevTools

Happy trading! 📈
