# Tools Module Documentation

Modular LangChain tools for AI agent market data interactions.

## 📁 Module Structure

```
tools/
├── __init__.py              # Package exports & ta_tools list
├── schemas.py               # Input schemas (40 lines)
├── market_data_tool.py      # Market data fetching (80 lines)
├── indicators_tool.py       # Technical indicators (100 lines)
├── patterns_tool.py         # Pattern detection (100 lines)
├── backtest_tool.py         # Backtesting (100 lines)
└── README.md                # This file
```

**Total: 7 files, ~420 lines organized**

---

## 🎯 Core Components

### 1. GetMarketDataTool (`market_data_tool.py`)

Fetch real-time market data for stocks.

**Features:**
- Current price, open, high, low
- Trading volume
- Price change and percentage change

**Usage:**

```python
from src.ai_agent.tools import GetMarketDataTool

tool = GetMarketDataTool()
result = tool._run(ticker="AAPL", period="6mo")
print(result)
```

**Output:**
```
Market Data for AAPL:
Current Price: $178.50
Open: $177.25
High: $179.00
Low: $176.80
Volume: 52,345,678
Previous Close: $177.00
Change: $1.50 (+0.85%)
```

### 2. GetTechnicalIndicatorsTool (`indicators_tool.py`)

Calculate technical indicators for stocks.

**Features:**
- RSI (Relative Strength Index) with interpretation
- MACD (Moving Average Convergence Divergence)
- MACD Signal and Histogram
- Buy/Sell/Hold signals

**Usage:**

```python
from src.ai_agent.tools import GetTechnicalIndicatorsTool

tool = GetTechnicalIndicatorsTool()
result = tool._run(ticker="RELIANCE.NS", period="6mo")
print(result)
```

**Output:**
```
Technical Indicators for RELIANCE.NS:
RSI (14): 65.23 - Neutral
MACD: 1.2345
MACD Signal: 1.1234
MACD Histogram: 0.1111
Signal: BUY
```

### 3. DetectPatternsTool (`patterns_tool.py`)

Detect technical chart patterns.

**Features:**
- Bullish breakout detection (price above 20-day high)
- Bearish breakdown detection (price below 20-day low)
- Moving average analysis (20-day, 50-day)
- Trend identification

**Usage:**

```python
from src.ai_agent.tools import DetectPatternsTool

tool = DetectPatternsTool()
result = tool._run(ticker="MSFT", period="6mo")
print(result)
```

**Output:**
```
Pattern Detection for MSFT:

⚠️ BULLISH BREAKOUT detected (price above 20-day high)

Price: $378.50
20-day SMA: $365.20
50-day SMA: $352.80
Trend: Bullish (Strong uptrend)
```

### 4. CalculateBacktestTool (`backtest_tool.py`)

Run backtests on trading strategies.

**Features:**
- RSI + MACD strategy backtesting
- Total return calculation
- Max drawdown analysis
- Signal counting (buy/sell)

**Usage:**

```python
from src.ai_agent.tools import CalculateBacktestTool

tool = CalculateBacktestTool()
result = tool._run(ticker="GOOGL", period="1y")
print(result)
```

**Output:**
```
Backtest Results for GOOGL (1y):

Initial Capital: $100,000
Final Equity: $115,230
Total Return: 15.23%
Max Drawdown: -8.45%

Signals Generated:
- Buy Signals: 8
- Sell Signals: 7
- Total Trades: 15

Strategy: RSI + MACD based signals
- RSI thresholds: 30 (oversold) / 70 (overbought)
- MACD crossover strategy
```

### 5. Input Schemas (`schemas.py`)

Pydantic models for tool inputs.

**TickerInput:**
```python
from src.ai_agent.tools import TickerInput

# Used by most tools
input_data = TickerInput(ticker="AAPL", period="6mo")
```

**BacktestInput:**
```python
from src.ai_agent.tools.schemas import BacktestInput

# For backtesting with custom capital
input_data = BacktestInput(
    ticker="AAPL",
    period="1y",
    initial_capital=50000.0
)
```

---

## 🔄 Using Tools Collection

### All Tools at Once

```python
from src.ai_agent.tools import ta_tools

# ta_tools is a list of all tool instances
for tool in ta_tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
```

### With LangChain Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from src.ai_agent.tools import ta_tools

# Initialize LLM
llm = ChatGroq(model="llama-3.1-70b-versatile", groq_api_key="...")

# Create agent with tools
agent = initialize_agent(
    tools=ta_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
result = agent.run("Analyze AAPL stock with technical indicators and patterns")
print(result)
```

---

## 📊 Tool Comparison

| Tool | Purpose | Output | Time |
|------|---------|--------|------|
| GetMarketDataTool | Current prices & volume | Price data | Fast |
| GetTechnicalIndicatorsTool | RSI, MACD, signals | Indicators | Fast |
| DetectPatternsTool | Breakouts, trends | Patterns | Fast |
| CalculateBacktestTool | Strategy performance | Returns, trades | Slow |

---

## 🎨 Architecture Benefits

### 1. Separation of Concerns ✅

Each tool has ONE clear purpose:
- `market_data_tool.py` → Fetch market data only
- `indicators_tool.py` → Calculate indicators only
- `patterns_tool.py` → Detect patterns only
- `backtest_tool.py` → Run backtests only

### 2. Easy Testing ✅

Test each tool independently:

```python
# Test market data tool
def test_market_data_tool():
    tool = GetMarketDataTool()
    result = tool._run("AAPL", "6mo")
    assert "Current Price" in result
    assert "AAPL" in result

# Test indicators tool
def test_indicators_tool():
    tool = GetTechnicalIndicatorsTool()
    result = tool._run("MSFT", "6mo")
    assert "RSI" in result
    assert "MACD" in result

# Test patterns tool
def test_patterns_tool():
    tool = DetectPatternsTool()
    result = tool._run("GOOGL", "6mo")
    assert "Pattern Detection" in result
```

### 3. Extensibility ✅

Add new tools easily:

```python
# tools/sentiment_tool.py
from langchain_core.tools import BaseTool
from .schemas import TickerInput

class GetSentimentTool(BaseTool):
    name = "get_sentiment"
    description = "Analyze market sentiment for a stock"
    args_schema = TickerInput
    
    def _run(self, ticker: str, period: str = "1mo") -> str:
        # Sentiment analysis logic
        return f"Sentiment for {ticker}: Positive"

# Add to __init__.py
from .sentiment_tool import GetSentimentTool

ta_tools.append(GetSentimentTool())
```

---

## 🚀 Usage Examples

### Example 1: Single Tool Usage

```python
from src.ai_agent.tools import GetMarketDataTool

tool = GetMarketDataTool()

# Analyze US stock
result = tool._run("AAPL", "3mo")
print(result)

# Analyze Indian stock
result = tool._run("RELIANCE.NS", "6mo")
print(result)
```

### Example 2: Multiple Tools Analysis

```python
from src.ai_agent.tools import (
    GetMarketDataTool,
    GetTechnicalIndicatorsTool,
    DetectPatternsTool
)

ticker = "MSFT"

# Get market data
market_tool = GetMarketDataTool()
market_data = market_tool._run(ticker, "6mo")

# Get indicators
indicators_tool = GetTechnicalIndicatorsTool()
indicators = indicators_tool._run(ticker, "6mo")

# Detect patterns
patterns_tool = DetectPatternsTool()
patterns = patterns_tool._run(ticker, "6mo")

print("=== MARKET DATA ===")
print(market_data)
print("\n=== INDICATORS ===")
print(indicators)
print("\n=== PATTERNS ===")
print(patterns)
```

### Example 3: Batch Analysis

```python
from src.ai_agent.tools import GetTechnicalIndicatorsTool

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
tool = GetTechnicalIndicatorsTool()

for ticker in tickers:
    print(f"\n{'='*50}")
    print(f"Analyzing {ticker}")
    print('='*50)
    result = tool._run(ticker, "6mo")
    print(result)
```

### Example 4: Backtesting Multiple Strategies

```python
from src.ai_agent.tools import CalculateBacktestTool

tool = CalculateBacktestTool()
tickers = ['AAPL', 'RELIANCE.NS', 'TCS.NS']
periods = ['6mo', '1y', '2y']

results = {}
for ticker in tickers:
    results[ticker] = {}
    for period in periods:
        result = tool._run(ticker, period)
        results[ticker][period] = result

# Display best performing
for ticker, period_results in results.items():
    print(f"\nResults for {ticker}:")
    for period, result in period_results.items():
        print(f"  {period}: {result}")
```

### Example 5: With LangChain ReAct Agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from src.ai_agent.tools import ta_tools

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    groq_api_key="your_key_here",
    temperature=0
)

agent = initialize_agent(
    tools=ta_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Complex query that uses multiple tools
query = """
Analyze AAPL stock:
1. Get current market data
2. Calculate technical indicators
3. Detect any chart patterns
4. Based on all this, should I buy or sell?
"""

response = agent.run(query)
print(response)
```

---

## 🔧 Configuration

### Error Handling

All tools include comprehensive error handling:

```python
try:
    result = tool._run("INVALID_TICKER", "6mo")
    # Returns error message, doesn't crash
except Exception as e:
    print(f"Error: {e}")
```

### Logging

Tools use Python logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now see detailed logs
tool = GetMarketDataTool()
result = tool._run("AAPL", "6mo")
```

### Custom Parameters

```python
# Different time periods
tool = GetMarketDataTool()
result = tool._run("AAPL", period="1mo")   # 1 month
result = tool._run("AAPL", period="1y")    # 1 year
result = tool._run("AAPL", period="5y")    # 5 years

# Multi-market support
result = tool._run("AAPL")          # US
result = tool._run("RELIANCE.NS")   # India NSE
result = tool._run("TCS.BO")        # India BSE
result = tool._run("BP.L")          # UK
```

---

## 📝 API Reference

### GetMarketDataTool

**Methods:**
- `_run(ticker: str, period: str = "6mo") -> str`
- `_arun(ticker: str, period: str = "6mo") -> str` (async)

**Returns:** Current price, open, high, low, volume, change

### GetTechnicalIndicatorsTool

**Methods:**
- `_run(ticker: str, period: str = "6mo") -> str`
- `_arun(ticker: str, period: str = "6mo") -> str` (async)

**Returns:** RSI, MACD, signals, interpretation

### DetectPatternsTool

**Methods:**
- `_run(ticker: str, period: str = "6mo") -> str`
- `_arun(ticker: str, period: str = "6mo") -> str` (async)

**Returns:** Breakouts, trends, moving averages

### CalculateBacktestTool

**Methods:**
- `_run(ticker: str, period: str = "1y") -> str`
- `_arun(ticker: str, period: str = "1y") -> str` (async)

**Returns:** Return %, max drawdown, signal counts

---

## 🔍 Troubleshooting

### Issue: "No data found for ticker"

**Cause:** Invalid ticker or no data available  
**Solution:** Verify ticker symbol, check internet connection

### Issue: Import errors

**Old:**
```python
from src.ai_agent.agent_tools import ta_tools
```

**New:**
```python
from src.ai_agent.tools import ta_tools
```

### Issue: Slow backtest

**Cause:** Large time period  
**Solution:** Use shorter periods for faster results

---

## 📚 Related Documentation

- [Agents Module](../agents/README.md) - TA and Portfolio agents
- [Workflow Module](../workflow/README.md) - LangGraph workflows
- [RAG Module](../rag/README.md) - Document analysis

---

## ✨ Summary

**Tools Module provides:**
- ✅ 4 focused, modular tools
- ✅ Clean separation of concerns
- ✅ Easy to test independently
- ✅ LangChain compatible
- ✅ Multi-market support
- ✅ Comprehensive error handling

**Perfect for:**
- LangChain agents
- Custom workflows
- Market analysis
- Trading strategies

---

**Version:** 2.0  
**Last Updated:** January 2026  
**Status:** Production Ready
