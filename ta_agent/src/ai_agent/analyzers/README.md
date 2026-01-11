# LLM Analyzers Package

**AI-powered market analysis using LangChain and LLMs**

## 📁 Package Structure

```
analyzers/
├── __init__.py                  # Package exports
├── llm_market_analyzer.py       # Main LLM market analyzer
├── multi_agent_analyzer.py      # Multi-agent system
├── agents.py                    # Specialized agents
├── prompts.py                   # Centralized prompts
└── README.md                    # This file
```

---

## 🎯 Architecture

### **Module Responsibilities:**

| Module | Responsibility | Lines |
|--------|---------------|-------|
| `llm_market_analyzer.py` | Single LLM analyzer for market insights | ~120 |
| `multi_agent_analyzer.py` | Multi-agent orchestration & synthesis | ~130 |
| `agents.py` | Specialized agents (Technical, Sentiment, Risk) | ~130 |
| `prompts.py` | All LLM prompts centralized | ~120 |

**Total:** ~500 lines (vs original 200 lines, better organized with more features)

---

## 🚀 Quick Start

### **1. LLMMarketAnalyzer (Single Agent)**

```python
from src.ai_agent.analyzers import LLMMarketAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = LLMMarketAnalyzer()

# Analyze market data
df = fetch_ohlcv('AAPL', period='3mo')
df = calculate_indicators(df)

# Get comprehensive analysis
analysis = analyzer.analyze_market_data(df, 'AAPL')
print(analysis)

# Generate trading strategy
strategy = analyzer.generate_trading_strategy(analysis, risk_tolerance='moderate')
print(strategy)

# Explain indicators
indicators = {
    'RSI': 58.5,
    'MACD': 2.45,
    'SMA_50': 175.20
}
explanation = analyzer.explain_indicators(indicators)
print(explanation)
```

### **2. MultiAgentAnalyzer (Multiple Specialized Agents)**

```python
from src.ai_agent.analyzers import MultiAgentAnalyzer

# Initialize multi-agent system
multi_analyzer = MultiAgentAnalyzer()

# Run comprehensive analysis with all agents
result = multi_analyzer.analyze(df, ticker='AAPL')

print("Technical Insights:", result['technical'])
print("Sentiment Insights:", result['sentiment'])
print("Risk Assessment:", result['risk'])
print("Synthesized Recommendation:", result['synthesis'])

# Get consensus view
consensus = multi_analyzer.get_agent_consensus(df)
print(f"Consensus: {consensus['consensus']}")
print(f"Confidence: {consensus['confidence']}%")
```

### **3. Individual Agents**

```python
from src.ai_agent.analyzers import TechnicalAgent, SentimentAgent, RiskAgent

# Use individual agents
tech_agent = TechnicalAgent()
sent_agent = SentimentAgent()
risk_agent = RiskAgent()

tech_insights = tech_agent.analyze(df)
sent_insights = sent_agent.analyze(df)
risk_insights = risk_agent.analyze(df)
```

---

## 📊 Component Details

### **1. LLMMarketAnalyzer**

**Purpose:** Single LLM for comprehensive market analysis

**Methods:**
- `analyze_market_data(df, ticker)` - Full technical analysis
- `generate_trading_strategy(analysis, risk_tolerance)` - Strategy generation
- `explain_indicators(indicator_data)` - Simple indicator explanations

**Use Cases:**
- Quick market insights
- Educational explanations
- Strategy generation
- Single-perspective analysis

**Example Output:**
```
Market Sentiment: Bullish

Key Technical Observations:
- RSI at 58.5 indicates neutral to slightly bullish momentum
- MACD showing bullish crossover above signal line
- Price trading above 50 and 200-day moving averages

Potential Trade Setup:
- Entry: Current levels around $182
- Stop Loss: Below $175 support
- Target: $195 resistance

Risk Factors:
- Market volatility increasing
- Overbought conditions if RSI crosses 70

Short-term Outlook: Positive bias for 1-2 weeks
```

---

### **2. MultiAgentAnalyzer**

**Purpose:** Multi-agent system with specialized perspectives

**Agents:**
- **TechnicalAgent:** Chart patterns, indicators, support/resistance
- **SentimentAgent:** Market momentum, trend strength, psychology
- **RiskAgent:** Volatility, risk factors, protective measures

**Methods:**
- `analyze(df, ticker)` - Run all agents + synthesis
- `synthesize_insights(technical, sentiment, risk)` - Combine perspectives
- `get_agent_consensus(df)` - Consensus view with confidence

**Use Cases:**
- Comprehensive multi-perspective analysis
- Risk-aware decision making
- Consensus building
- Conflict detection between signals

**Example Output:**
```python
{
    'technical': 'Strong bullish signals from RSI and MACD...',
    'sentiment': 'Positive momentum with uptrend intact...',
    'risk': 'Moderate volatility, key support at $175...',
    'synthesis': 'All agents agree on bullish outlook. Recommend BUY...',
    'consensus': 'BULLISH',
    'confidence': 85.0,
    'agreement': {
        'bullish_signals': 3,
        'bearish_signals': 0
    }
}
```

---

### **3. Specialized Agents**

#### **TechnicalAgent**

**Focus:** Chart patterns, technical indicators, support/resistance

**Analyzes:**
- RSI, MACD, moving averages
- Volume patterns
- Price levels
- Trend strength

**Output Example:**
```
Technical signals are bullish:
- RSI at 58 showing healthy momentum
- MACD bullish crossover confirmed
- Price above all major moving averages
- Volume supporting the move

Recommendation: Look for pullbacks to 50-day SMA for entries
```

---

#### **SentimentAgent**

**Focus:** Market momentum, trend strength, market psychology

**Analyzes:**
- Trend direction and strength
- Volatility patterns
- Momentum indicators
- Market psychology

**Output Example:**
```
Market sentiment is positive:
- Strong uptrend established
- Volatility declining (bullish)
- Momentum accelerating
- Fear turning to greed

Watch for: Complacency at highs, RSI overbought
```

---

#### **RiskAgent**

**Focus:** Risk assessment, volatility, protective measures

**Analyzes:**
- Volatility levels
- Price ranges
- Risk/reward ratios
- Protective stop levels

**Output Example:**
```
Risk assessment:
- Volatility: 28% (moderate)
- 20-day range: $175-$185
- Key support: $175
- Risk level: Moderate

Protective measures:
- Use 5% stop loss
- Position size: 3-5% of portfolio
- Monitor support at $175
```

---

## 🔄 Data Flow

### **LLMMarketAnalyzer Flow:**
```
Market Data → Calculate Metrics → Build Prompt → LLM → Analysis
```

### **MultiAgentAnalyzer Flow:**
```
Market Data
     ↓
┌────┴────┬────────┐
↓         ↓        ↓
Technical Sentiment Risk
Agent     Agent    Agent
↓         ↓        ↓
└────┬────┴────────┘
     ↓
Synthesis LLM
     ↓
Unified Recommendation
```

---

## 🎨 Customization

### **Custom Prompts:**

Edit [prompts.py](prompts.py) to customize agent behavior:

```python
# Custom technical agent prompt
TECHNICAL_AGENT_SYSTEM = "You are a momentum trader focused on breakouts..."

# Custom risk tolerance
TRADING_STRATEGY_TEMPLATE = """Create a {risk_tolerance} strategy...
For conservative: 2% risk per trade
For moderate: 5% risk per trade
For aggressive: 10% risk per trade
"""
```

### **Custom Models:**

```python
# Use different models for different agents
tech_agent = TechnicalAgent(model="llama-3.3-70b-versatile")
sent_agent = SentimentAgent(model="openai/gpt-oss-120b")
risk_agent = RiskAgent(model="mixtral-8x7b-32768")
```

### **Custom Temperature:**

```python
# More creative analysis
analyzer = LLMMarketAnalyzer(temperature=0.7)

# More deterministic analysis
analyzer = LLMMarketAnalyzer(temperature=0.1)
```

---

## 🧪 Testing

### **Unit Testing:**

```python
import pytest
from src.ai_agent.analyzers import TechnicalAgent

def test_technical_agent():
    agent = TechnicalAgent()
    df = create_mock_dataframe()
    
    result = agent.analyze(df)
    
    assert isinstance(result, str)
    assert len(result) > 100  # Should have substantial output
    assert any(word in result.lower() for word in ['bullish', 'bearish', 'neutral'])
```

### **Integration Testing:**

```python
def test_multi_agent_analysis():
    analyzer = MultiAgentAnalyzer()
    df = fetch_ohlcv('AAPL', period='1mo')
    
    result = analyzer.analyze(df, 'AAPL')
    
    assert 'technical' in result
    assert 'sentiment' in result
    assert 'risk' in result
    assert 'synthesis' in result
```

---

## 🔗 Integration with Other Modules

### **With Autonomous Agents:**

```python
from src.ai_agent.agents import AutonomousTAAgent
from src.ai_agent.analyzers import MultiAgentAnalyzer

# Combine LangChain agent with multi-agent analyzer
ta_agent = AutonomousTAAgent()
multi_analyzer = MultiAgentAnalyzer()

# Get tool-based analysis
tool_result = ta_agent.run(f"Analyze AAPL", ticker='AAPL')

# Get LLM-based multi-agent analysis
llm_result = multi_analyzer.analyze(df, 'AAPL')

# Combine both perspectives
```

### **With RAG Integration:**

```python
from src.ai_agent.rag_integration import IntegratedRAGAgent
from src.ai_agent.analyzers import LLMMarketAnalyzer

rag_agent = IntegratedRAGAgent()
llm_analyzer = LLMMarketAnalyzer()

# Combine document insights with LLM analysis
```

---

## 📚 Use Cases

### **1. Quick Market Analysis:**
```python
analyzer = LLMMarketAnalyzer()
analysis = analyzer.analyze_market_data(df, 'AAPL')
```

### **2. Comprehensive Multi-Perspective:**
```python
multi = MultiAgentAnalyzer()
result = multi.analyze(df, 'AAPL')
print(result['synthesis'])
```

### **3. Educational Explanations:**
```python
analyzer = LLMMarketAnalyzer()
explanation = analyzer.explain_indicators({'RSI': 65, 'MACD': 1.5})
```

### **4. Strategy Generation:**
```python
analyzer = LLMMarketAnalyzer()
analysis = analyzer.analyze_market_data(df, 'AAPL')
strategy = analyzer.generate_trading_strategy(analysis, 'aggressive')
```

### **5. Consensus Building:**
```python
multi = MultiAgentAnalyzer()
consensus = multi.get_agent_consensus(df)
if consensus['confidence'] > 70:
    print(f"Strong {consensus['consensus']} consensus")
```

---

## ⚙️ Configuration

### **Environment Variables:**

```bash
# Required
GROQ_API_KEY=your_groq_api_key

# Optional (defaults shown)
LLM_MODEL=openai/gpt-oss-120b
LLM_TEMPERATURE=0.3
```

### **Model Options:**

Available Groq models:
- `openai/gpt-oss-120b` - Fast, good quality (default)
- `llama-3.3-70b-versatile` - Versatile, balanced
- `mixtral-8x7b-32768` - Long context
- `gemma2-9b-it` - Compact, fast

---

## 🎯 Benefits of Modular Structure

| Aspect | Before | After |
|--------|--------|-------|
| **Organization** | 2 classes in 1 file (200 lines) | 4 modules (500 lines) |
| **Prompts** | Inline in methods | Centralized in prompts.py |
| **Agents** | Mixed in one class | Separate agent classes |
| **Testing** | Test entire system | Test individual agents |
| **Customization** | Modify code | Edit prompts.py |
| **Reusability** | Tightly coupled | Independent components |

---

## 📝 API Reference

### **LLMMarketAnalyzer**

```python
class LLMMarketAnalyzer:
    def __init__(model: str, temperature: float)
    def analyze_market_data(df: pd.DataFrame, ticker: str) -> str
    def generate_trading_strategy(analysis: str, risk_tolerance: str) -> str
    def explain_indicators(indicator_data: Dict[str, float]) -> str
```

### **MultiAgentAnalyzer**

```python
class MultiAgentAnalyzer:
    def __init__(model: str, temperature: float)
    def analyze(df: pd.DataFrame, ticker: str) -> Dict[str, str]
    def synthesize_insights(technical: str, sentiment: str, risk: str) -> str
    def get_agent_consensus(df: pd.DataFrame) -> Dict[str, any]
```

### **Specialized Agents**

```python
class TechnicalAgent:
    def __init__(model: str, temperature: float)
    def analyze(df: pd.DataFrame) -> str

class SentimentAgent:
    def __init__(model: str, temperature: float)
    def analyze(df: pd.DataFrame) -> str

class RiskAgent:
    def __init__(model: str, temperature: float)
    def analyze(df: pd.DataFrame) -> str
```

---

**Created:** January 2026  
**Status:** ✅ Production Ready  
**Maintainer:** Technical Analyst Agent Team
