# Multi-Agent Coordinator Package

**Modular multi-agent analysis system combining Technical Analysis + Sentiment Analysis + Risk Assessment**

## 📁 Package Structure

```
coordinator/
├── __init__.py                      # Package exports
├── multi_agent_coordinator.py       # Main orchestrator
├── technical_analyzer.py            # Technical analysis module
├── risk_analyzer.py                 # Risk assessment module
├── scoring.py                       # Composite scoring engine
├── recommendation_engine.py         # Recommendation generation
├── constants.py                     # Configuration & thresholds
└── README.md                        # This file
```

---

## 🎯 Architecture Overview

### **Separation of Concerns:**

| Module | Responsibility | Lines |
|--------|---------------|-------|
| `multi_agent_coordinator.py` | Orchestration & data flow | ~150 |
| `technical_analyzer.py` | Technical indicators & scoring | ~180 |
| `risk_analyzer.py` | Risk metrics & assessment | ~140 |
| `scoring.py` | Composite score calculation | ~110 |
| `recommendation_engine.py` | Trading recommendations | ~160 |
| `constants.py` | Configuration & thresholds | ~80 |

**Total:** ~820 lines (vs original 520 lines monolithic)  
**Benefits:** Better organization, easier testing, clearer responsibilities

---

## 🚀 Quick Start

### **Basic Usage:**

```python
from src.ai_agent.coordinator import MultiAgentCoordinator

# Initialize coordinator
coordinator = MultiAgentCoordinator(api_keys={
    'newsapi': 'your_newsapi_key',
    'finnhub': 'your_finnhub_key'
})

# Single stock comprehensive analysis
result = coordinator.comprehensive_analysis(
    ticker='AAPL',
    period='1y',
    include_sentiment=True
)

print(f"Action: {result['recommendation']['action']}")
print(f"Confidence: {result['confidence']}%")
print(f"Score: {result['composite_score']}")
```

### **Batch Analysis:**

```python
# Analyze multiple stocks
tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
results = coordinator.batch_analysis(tickers)

for ticker, analysis in results.items():
    if 'error' not in analysis:
        print(f"{ticker}: {analysis['recommendation']['action']}")
```

### **Custom Weights:**

```python
# Customize analysis weights
custom_weights = {
    'technical': 0.50,  # 50% weight on technical
    'sentiment': 0.30,  # 30% weight on sentiment
    'risk': 0.20        # 20% weight on risk
}

result = coordinator.comprehensive_analysis(
    ticker='AAPL',
    custom_weights=custom_weights
)
```

---

## 📊 Component Details

### **1. MultiAgentCoordinator (Main Orchestrator)**

**Purpose:** Coordinates all analysis modules and manages data flow

**Methods:**
- `comprehensive_analysis()` - Full 360° analysis
- `batch_analysis()` - Analyze multiple tickers
- `_build_result()` - Assemble final result dictionary

**Example:**
```python
coordinator = MultiAgentCoordinator(api_keys)
result = coordinator.comprehensive_analysis('AAPL')
```

---

### **2. TechnicalAnalyzer**

**Purpose:** Analyzes technical indicators and generates technical scores

**Analyzes:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Moving Averages (SMA 20, 50, 200)
- Support/Resistance levels
- Trend detection (Golden/Death Cross)

**Methods:**
- `analyze()` - Main analysis method
- `_calculate_technical_score()` - Score calculation
- `_determine_trend()` - Trend identification
- `_classify_score()` - Label classification

**Example:**
```python
from src.ai_agent.coordinator import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()
result = analyzer.analyze('AAPL', df)
print(f"Technical Score: {result['score']}")
print(f"Trend: {result['trend']}")
print(f"Signals: {result['signals']}")
```

**Output:**
```python
{
    'score': 0.45,  # -1 to +1
    'label': 'Bullish',
    'trend': 'Strong Uptrend',
    'indicators': {
        'rsi': 58.5,
        'macd': 2.45,
        'sma_20': 180.50,
        'sma_50': 175.20,
        'sma_200': 165.80,
        'close': 182.30
    },
    'signals': [
        'RSI Neutral (Positive)',
        'MACD Bullish Crossover',
        'Above 200 SMA (Strong Bullish)',
        'Golden Cross (Very Bullish)'
    ],
    'support': 175.20,
    'resistance': 185.50,
    'recommendation': 'BUY'
}
```

---

### **3. RiskAnalyzer**

**Purpose:** Assesses risk metrics and generates risk scores

**Analyzes:**
- Volatility (annualized standard deviation)
- Maximum Drawdown
- Beta (market correlation)
- Overall risk level

**Methods:**
- `analyze()` - Main risk assessment
- `_calculate_volatility()` - Annualized volatility
- `_calculate_max_drawdown()` - Maximum drawdown
- `_calculate_beta()` - Beta calculation
- `_calculate_risk_score()` - Overall risk score

**Example:**
```python
from src.ai_agent.coordinator import RiskAnalyzer

analyzer = RiskAnalyzer()
result = analyzer.analyze('AAPL', df)
print(f"Risk Level: {result['risk_level']}")
print(f"Volatility: {result['volatility']}%")
```

**Output:**
```python
{
    'score': 0.65,  # -1 to +1 (higher = less risky)
    'risk_level': 'Moderate',
    'volatility': 28.5,  # Annualized %
    'max_drawdown': -15.3,  # %
    'beta': 1.15,
    'risk_score': 35,  # 0-100 (lower = less risky)
    'recommendation': 'Caution'
}
```

---

### **4. CompositeScorer**

**Purpose:** Combines multiple analysis scores with configurable weights

**Features:**
- Weighted score combination
- Confidence calculation based on agreement
- Score classification

**Methods:**
- `calculate_composite()` - Weighted composite score
- `_calculate_confidence()` - Confidence based on variance
- `_classify_score()` - Label classification

**Example:**
```python
from src.ai_agent.coordinator import CompositeScorer

scorer = CompositeScorer()
composite = scorer.calculate_composite(
    technical={'score': 0.45},
    sentiment={'composite_score': 0.35, 'confidence': 0.8},
    risk={'score': 0.65},
    weights={'technical': 0.4, 'sentiment': 0.35, 'risk': 0.25}
)
print(f"Composite: {composite['score']}, Confidence: {composite['confidence']}")
```

**Output:**
```python
{
    'score': 0.47,  # Weighted average
    'label': 'Buy Signal',
    'confidence': 0.72,  # Based on agreement
    'components': {
        'technical': 0.45,
        'sentiment': 0.35,
        'risk': 0.65
    }
}
```

---

### **5. RecommendationEngine**

**Purpose:** Generates actionable trading recommendations

**Produces:**
- Action (STRONG BUY, BUY, HOLD, SELL, STRONG SELL)
- Entry/Exit Strategy
- Stop Loss & Take Profit levels
- Risk/Reward ratio
- Position sizing advice
- Time horizon

**Methods:**
- `generate_recommendation()` - Main recommendation
- `_determine_action()` - Action & reasoning
- `_calculate_entry_strategy()` - Entry/exit points
- `_calculate_position_sizing()` - Position size
- `_determine_time_horizon()` - Time horizon

**Example:**
```python
from src.ai_agent.coordinator import RecommendationEngine

engine = RecommendationEngine()
recommendation = engine.generate_recommendation(
    ticker='AAPL',
    technical=technical_result,
    sentiment=sentiment_result,
    risk=risk_result,
    composite=composite_result
)
print(f"Action: {recommendation['action']}")
print(f"Entry: ${recommendation['entry_strategy']['target_price']}")
```

**Output:**
```python
{
    'action': 'BUY',
    'confidence': 72.0,
    'reasoning': 'Positive signals with good confidence',
    'entry_strategy': {
        'target_price': 182.30,
        'stop_loss': 170.50,
        'take_profit_1': 190.00,
        'take_profit_2': 209.00,
        'risk_reward_ratio': 2.25
    },
    'position_sizing': '3-5% of portfolio',
    'time_horizon': '3-6 months',
    'key_levels': {
        'support': 175.20,
        'resistance': 190.00,
        'current': 182.30
    }
}
```

---

### **6. Constants & Configuration**

**Purpose:** Centralized configuration for all thresholds and weights

**Includes:**
- `DEFAULT_WEIGHTS` - Default analysis weights
- `SCORE_THRESHOLDS` - Classification thresholds
- `RISK_THRESHOLDS` - Risk assessment thresholds
- `RECOMMENDATION_THRESHOLDS` - Action determination
- `POSITION_SIZING` - Position size templates
- `RSI_THRESHOLDS` - RSI overbought/oversold
- Stop loss/take profit multipliers

**Example:**
```python
from src.ai_agent.coordinator import DEFAULT_WEIGHTS, SCORE_THRESHOLDS

print(DEFAULT_WEIGHTS)
# {'technical': 0.40, 'sentiment': 0.35, 'risk': 0.25}

print(SCORE_THRESHOLDS['composite'])
# {'strong_buy': 0.4, 'buy': 0.15, 'neutral_high': -0.15, 'sell': -0.4}
```

---

## 🔄 Data Flow

```
User Request
     ↓
MultiAgentCoordinator.comprehensive_analysis()
     ↓
┌────┴─────────────────────┐
↓                          ↓
Fetch OHLCV Data    Calculate Indicators
     ↓                          ↓
     └────────┬─────────────────┘
              ↓
    ┌─────────┴─────────┐
    ↓         ↓         ↓
Technical  Sentiment  Risk
Analyzer   Agent      Analyzer
    ↓         ↓         ↓
    └─────────┬─────────┘
              ↓
      CompositeScorer
      (Weighted Combination)
              ↓
    RecommendationEngine
    (Entry/Exit Strategy)
              ↓
       Final Result
```

---

## 🧪 Testing

### **Unit Testing Individual Modules:**

```python
import pytest
from src.ai_agent.coordinator import TechnicalAnalyzer

def test_technical_analyzer():
    analyzer = TechnicalAnalyzer()
    # Create mock DataFrame with indicators
    df = create_mock_dataframe()
    result = analyzer.analyze('TEST', df)
    
    assert 'score' in result
    assert -1 <= result['score'] <= 1
    assert result['label'] in ['Very Bullish', 'Bullish', 'Neutral', 'Bearish', 'Very Bearish']
```

### **Integration Testing:**

```python
def test_full_analysis():
    coordinator = MultiAgentCoordinator()
    result = coordinator.comprehensive_analysis('AAPL', period='1mo')
    
    assert result['ticker'] == 'AAPL'
    assert 'composite_score' in result
    assert 'recommendation' in result
    assert result['recommendation']['action'] in ['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL']
```

---

## 📈 API Integration

The coordinator is used by [comprehensive.py](../../../api/v1/endpoints/comprehensive.py) endpoints:

```python
from src.ai_agent.coordinator import MultiAgentCoordinator

# API endpoint
@router.get("/analysis/{ticker}")
async def comprehensive_analysis(ticker: str):
    coordinator = MultiAgentCoordinator(api_keys)
    return coordinator.comprehensive_analysis(ticker)
```

**Available Endpoints:**
- `GET /api/v1/analysis/{ticker}` - Single stock analysis
- `POST /api/v1/analysis/batch` - Batch analysis
- `GET /api/v1/analysis/{ticker}/technical-only` - Technical only
- `GET /api/v1/analysis/{ticker}/comparison` - Peer comparison
- `GET /api/v1/analysis/portfolio/analyze` - Portfolio analysis

---

## ⚙️ Configuration

### **Customize Weights:**

```python
custom_weights = {
    'technical': 0.50,
    'sentiment': 0.30,
    'risk': 0.20
}

result = coordinator.comprehensive_analysis('AAPL', custom_weights=custom_weights)
```

### **Customize Thresholds:**

Edit [constants.py](constants.py) to adjust:
- RSI overbought/oversold levels
- Score classification thresholds
- Risk level boundaries
- Position sizing templates

---

## 🔧 Extending the System

### **Add New Analyzer:**

1. Create new analyzer module (e.g., `fundamental_analyzer.py`)
2. Implement `analyze()` method returning score dictionary
3. Update `CompositeScorer` to include new score
4. Update `DEFAULT_WEIGHTS` in `constants.py`
5. Update `MultiAgentCoordinator` to call new analyzer

**Example:**
```python
# fundamental_analyzer.py
class FundamentalAnalyzer:
    def analyze(self, ticker: str, data: Dict) -> Dict:
        # Analyze P/E, P/B, debt ratios, etc.
        return {
            'score': 0.35,
            'label': 'Undervalued',
            'metrics': {...}
        }
```

---

## 📚 Additional Resources

- **API Documentation:** See [comprehensive.py](../../../api/v1/endpoints/comprehensive.py)
- **Sentiment Analysis:** See [../../../sentiment/](../../../sentiment/)
- **Technical Indicators:** See [../../../indicators/](../../../indicators/)
- **Risk Metrics:** See [../../../backtest/](../../../backtest/)

---

## 🎉 Benefits of Modular Structure

| Aspect | Monolithic | Modular |
|--------|-----------|---------|
| **Maintainability** | 520 lines in 1 file | ~150 lines per module |
| **Testing** | Test entire system | Test individual components |
| **Readability** | All logic mixed | Clear separation |
| **Extensibility** | Hard to add features | Easy to add analyzers |
| **Debugging** | Find issues in 520 lines | Target specific module |
| **Reusability** | Tightly coupled | Independent modules |

---

**Created:** January 2026  
**Status:** ✅ Production Ready  
**Maintainer:** Technical Analyst Agent Team
