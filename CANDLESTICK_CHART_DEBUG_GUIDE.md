# 🔍 Candlestick Chart Debugging Guide

## Problem
Candlestick charts are not showing in the UI during stock analysis, even though they were visible before.

## Root Cause Analysis

The issue can be caused by one of these reasons:

### 1. **Backend not returning chart data**
   - API endpoint might not be including `price_data` and `indicator_data` in response
   - Data might be empty arrays

### 2. **Frontend conditional rendering blocking the chart**
   - The condition `{result.price_data && result.indicator_data &&` might fail
   - Data might not be in expected format
   - The collapse section might be closed

### 3. **Chart library issues**
   - `react-apexcharts` might not be installed or working
   - ApexCharts might have errors in console

## Changes Made

### ✅ Fixed Files:

#### 1. **ResultDisplay.tsx** (Modified)
- Added array validation: `Array.isArray(result.price_data) && result.price_data.length > 0`
- Added patterns prop: `patterns={result.patterns || []}`
- Added debug alerts to show if data is missing

#### 2. **StockCharts.tsx** (Modified)
- Added data validation at component start
- Added console logging to debug data issues
- Added error messages showing what data was received

## How to Debug

### Step 1: Check Browser Console

1. Open browser Developer Tools (Press `F12`)
2. Go to **Console** tab
3. Look for:
   - `StockCharts render:` - Shows data being passed to chart component
   - Any red errors related to Chart or ApexCharts
   - Network errors

**Expected output:**
```javascript
StockCharts render: {
  ticker: "HDFCBANK.NS",
  priceDataLength: 90,
  indicatorDataLength: 90,
  patternsLength: 2,
  firstPrice: { date: "2024-10-13", open: 1650.5, high: 1665.2, ... },
  firstIndicator: { date: "2024-10-13", rsi: 68.5, macd: -10.89, ... }
}
```

### Step 2: Check Network Tab

1. In Developer Tools, go to **Network** tab
2. Perform stock analysis query
3. Find the API request (look for `/ai/analyze` or similar)
4. Click on it and check **Response** tab

**What to look for:**
```json
{
  "id": 123,
  "query_text": "analyze HDFCBANK.NS",
  "query_type": "ai_analysis",
  "ticker": "HDFCBANK.NS",
  "result": {
    "ticker": "HDFCBANK.NS",
    "analysis": "Market Sentiment – Bearish...",
    "latest_price": 939.0,
    "rsi": 22.7,
    "macd": -10.8926,
    "signal": "HOLD",
    "price_data": [           ← MUST BE PRESENT
      {
        "date": "2024-10-13",
        "open": 1650.5,
        "high": 1665.2,
        "low": 1645.0,
        "close": 1658.3,
        "volume": 5234567
      },
      // ... more data points (should have 90+ items)
    ],
    "indicator_data": [       ← MUST BE PRESENT
      {
        "date": "2024-10-13",
        "rsi": 68.5,
        "macd": -10.89,
        "macd_signal": -5.03,
        "macd_hist": -5.86,
        "sma_20": 1650.2,
        "sma_50": 1680.5,
        // ... more indicators
      },
      // ... more data points
    ],
    "patterns": []
  }
}
```

**❌ If `price_data` or `indicator_data` is missing or empty** → Backend issue

### Step 3: Check for Warnings

After my changes, you should see warning alerts if data is missing:

- **"Chart data not available. Missing price_data in API response."** 
  → Backend is not returning `price_data`

- **"Chart data is empty. API returned 0 data points."**
  → Backend returns empty arrays

- **"No price data available for charting."**
  → Data validation failed in StockCharts component

### Step 4: Check if Section is Collapsed

1. Look for the section header: **"📊 Interactive Charts"**
2. Check if there's a collapse arrow (▼ or ▲)
3. Click on the header to expand/collapse
4. The chart should be expanded by default (set to `charts: true` in state)

## Quick Fixes

### Fix 1: If Backend Not Returning Data

**File:** `ta_agent/src/api/v1/endpoints/ai.py` (around line 120)

Check if this code exists:
```python
# Prepare historical data for charts (last 90 days or available data)
chart_data = df.tail(90).copy()
price_data = [
    {
        "date": idx.strftime('%Y-%m-%d'),
        "open": float(row['open']),
        "high": float(row['high']),
        "low": float(row['low']),
        "close": float(row['close']),
        "volume": int(row['volume']) if 'volume' in row else 0
    }
    for idx, row in chart_data.iterrows()
]

indicator_data = [
    {
        "date": idx.strftime('%Y-%m-%d'),
        "rsi": float(row.get('rsi', 0)) if not pd.isna(row.get('rsi', 0)) else None,
        "macd": float(row.get('macd', 0)) if not pd.isna(row.get('macd', 0)) else None,
        # ... more indicators
    }
    for idx, row in chart_data.iterrows()
]

# Include in result
result = {
    # ... other fields
    "price_data": price_data,
    "indicator_data": indicator_data,
    # ...
}
```

**If missing, backend needs to be updated to return this data.**

### Fix 2: If Chart Library Missing

```bash
cd ta-agent-frontend
npm install react-apexcharts apexcharts
```

### Fix 3: Force Chart to Always Show (Testing)

Temporarily modify `ResultDisplay.tsx`:

```tsx
{/* Remove the conditional - JUST FOR TESTING */}
<Box sx={{ mb: 3 }}>
  <Typography variant="h6">📊 Interactive Charts</Typography>
  <StockCharts 
    ticker={query.ticker || result.ticker || "TEST"}
    priceData={result.price_data || []}
    indicatorData={result.indicator_data || []}
    patterns={result.patterns || []}
  />
</Box>
```

This will show the chart component even if data is missing, so you can see the error messages.

## Testing Checklist

- [ ] Open browser console (F12)
- [ ] Perform stock analysis (e.g., "analyze HDFCBANK.NS")
- [ ] Check console for `StockCharts render:` log
- [ ] Check Network tab for API response with `price_data` and `indicator_data`
- [ ] Look for warning alerts in UI
- [ ] Check if "📊 Interactive Charts" section is visible
- [ ] Try clicking section header to expand/collapse
- [ ] Check for any red errors in console

## Expected Behavior After Fix

1. **When data is available:**
   - "📊 Interactive Charts" section appears
   - Section is expanded by default
   - Candlestick chart with controls is visible
   - Can toggle between Candlestick and Line chart
   - Can select date ranges (1m, 3m, 6m, 1y, All)
   - Can overlay indicators (SMA, EMA, Bollinger Bands)
   - Tabs show: Price Chart, RSI Indicator, MACD Indicator

2. **When data is missing:**
   - Warning alert shows why chart can't display
   - Console logs show what data was received
   - Error message indicates what to fix

## Next Steps

1. **Test the changes:**
   ```bash
   cd ta-agent-frontend
   npm start
   ```

2. **Run a stock analysis query** (e.g., "analyze AAPL" or "analyze HDFCBANK.NS")

3. **Check the console logs** to see what data is being received

4. **If data is missing:**
   - Backend issue: Check `ta_agent/src/api/v1/endpoints/ai.py`
   - Restart backend: `cd ta_agent && python -m uvicorn src.main:app --reload --port 8000`

5. **If data exists but chart not showing:**
   - Check for JavaScript errors in console
   - Verify `react-apexcharts` is installed
   - Check if section is collapsed (click header)

## Common Scenarios

### Scenario 1: "Chart data not available" warning shows
**Problem:** Backend not returning `price_data`
**Solution:** Update backend API endpoint to include chart data

### Scenario 2: Console shows `priceDataLength: 0`
**Problem:** Backend returns empty arrays
**Solution:** Check if stock ticker is valid and data fetch is working

### Scenario 3: Console shows `priceDataLength: undefined`
**Problem:** API response doesn't have the field at all
**Solution:** Backend needs to add `price_data` to response

### Scenario 4: Chart was showing before, suddenly stopped
**Possible causes:**
- Backend code was modified and removed chart data
- API endpoint changed
- Database cache is stale
- Frontend rebuild needed

**Solution:**
- Restart both backend and frontend
- Clear browser cache
- Check git history for recent changes

## Manual Test

Create a test query in browser console:

```javascript
// Test if StockCharts component can render with sample data
const testData = {
  ticker: "TEST",
  priceData: [
    { date: "2024-01-01", open: 100, high: 105, low: 98, close: 103, volume: 1000000 },
    { date: "2024-01-02", open: 103, high: 108, low: 102, close: 106, volume: 1200000 },
  ],
  indicatorData: [
    { date: "2024-01-01", rsi: 65, macd: 2.5, macd_signal: 2.0, macd_hist: 0.5, sma_20: 100, sma_50: 98 },
    { date: "2024-01-02", rsi: 68, macd: 2.8, macd_signal: 2.2, macd_hist: 0.6, sma_20: 101, sma_50: 99 },
  ],
  patterns: []
};

// This should render charts if component is working
```

## Files Modified

1. ✅ `ta-agent-frontend/src/components/dashboard/ResultDisplay.tsx`
   - Added data validation
   - Added debug alerts
   - Added patterns prop

2. ✅ `ta-agent-frontend/src/components/dashboard/StockCharts.tsx`
   - Added data validation
   - Added console logging
   - Added detailed error messages

## Rollback Instructions

If the changes cause issues, you can revert:

```bash
cd d:\Technical_Analyst_Agent
git checkout ta-agent-frontend/src/components/dashboard/ResultDisplay.tsx
git checkout ta-agent-frontend/src/components/dashboard/StockCharts.tsx
```

---

## Summary

The modifications add:
1. ✅ Better data validation
2. ✅ Console debugging logs
3. ✅ User-friendly error messages
4. ✅ Checks for array validity and length

**Now you can identify exactly why the chart isn't showing!**

Run the frontend, perform a stock analysis, and check the console/network tabs to see what's happening.
