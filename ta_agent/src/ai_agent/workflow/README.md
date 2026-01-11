# Workflow Module Documentation

Modular LangGraph-based workflow for comprehensive stock analysis.

## 📁 Module Structure

```
workflow/
├── __init__.py              # Package exports
├── states.py                # State definitions (30 lines)
├── prompts.py               # Workflow prompts (150 lines)
├── data_fetcher.py          # Data fetching (130 lines)
├── nodes/                   # Analysis nodes
│   ├── __init__.py
│   ├── technical_node.py    # Technical analysis (150 lines)
│   ├── risk_node.py         # Risk assessment (150 lines)
│   └── recommendation_node.py # Final recommendation (100 lines)
├── ta_workflow.py           # Main orchestrator (150 lines)
├── rag_analyzer.py          # Pattern analyzer (130 lines)
└── README.md                # This file
```

**Total: 10 files, ~900 lines organized**

---

## 🎯 Core Components

### 1. TAWorkflow (`ta_workflow.py`)

Main orchestrator that executes a 5-step analysis pipeline.

**Pipeline Steps:**
1. 📥 **Fetch Data** - Download 6 months of price data
2. 📊 **Fundamentals** - Get P/E, sector, market cap
3. 🔍 **Technical Analysis** - RSI, MACD, patterns (LLM)
4. ⚠️ **Risk Assessment** - Volatility, drawdown, ATR (LLM)
5. 💡 **Recommendation** - BUY/SELL/HOLD with levels (LLM)

**Usage:**

```python
from src.ai_agent.workflow import TAWorkflow

# Initialize workflow
workflow = TAWorkflow()

# Run analysis
result = workflow.analyze('AAPL')

# Access results
print(result['final_recommendation'])  # Human-readable
print(result['recommendation_structured'])  # JSON structure
print(result['messages'])  # Execution log
```

**Result Structure:**

```python
{
    'ticker': 'AAPL',
    'market_data': DataFrame(...),
    
    # Technical Analysis
    'technical_analysis': 'AAPL shows bullish momentum...',
    'technical_structured': {
        'patterns': ['ascending triangle'],
        'trend': {'direction': 'up', 'strength': 'high'},
        'support_levels': [150.0, 148.5],
        'resistance_levels': [155.0, 158.0],
        'confidence': 0.8
    },
    
    # Fundamental Context
    'fundamental_context': 'Apple Inc., Sector: Technology...',
    'fundamentals_structured': {
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'market_cap': 2500000000000,
        'pe': 28.5
    },
    
    # Risk Assessment
    'risk_assessment': 'Moderate volatility with 15% drawdown...',
    'risk_structured': {
        'volatility_20d_pct': 1.8,
        'max_drawdown_60d_pct': 15.2,
        'atr_14': 2.5,
        'position_sizing_rule': 'Max 5% of portfolio',
        'stop_loss_rule': 'Set at $145'
    },
    
    # Final Recommendation
    'final_recommendation': 'BUY recommendation with entry at $152...',
    'recommendation_structured': {
        'action': 'BUY',
        'entry_price': 152.0,
        'stop_loss': 145.0,
        'take_profit': [160.0, 165.0],
        'position_size_pct': 5.0,
        'time_horizon_days': 30
    },
    
    'messages': [
        '✓ Fetched data for AAPL',
        '✓ Fundamentals context fetched',
        '✓ Technical analysis complete',
        '✓ Risk assessment complete',
        '✓ Final recommendation generated'
    ]
}
```

### 2. AnalysisState (`states.py`)

TypedDict definition for workflow state.

**Usage:**

```python
from src.ai_agent.workflow import AnalysisState

# State is automatically managed by workflow
# You don't need to create it manually
```

### 3. WorkflowPrompts (`prompts.py`)

Centralized prompt management for all LLM interactions.

**Features:**
- System prompts for each analysis type
- JSON schemas for structured outputs
- Template methods with parameter substitution

**Usage:**

```python
from src.ai_agent.workflow.prompts import WorkflowPrompts

prompts = WorkflowPrompts()

# Get technical analysis prompt
tech_prompt = prompts.get_technical_prompt(
    ticker='AAPL',
    price=152.0,
    rsi=65.0,
    macd=1.2,
    signal='BUY',
    trend_20d=5.2,
    fundamentals='Apple Inc., Technology'
)

# Get risk assessment prompt
risk_prompt = prompts.get_risk_prompt(
    ticker='AAPL',
    volatility_20d=1.8,
    max_drawdown=15.2,
    atr_14=2.5,
    technical_summary='Bullish momentum...'
)
```

### 4. MarketDataFetcher (`data_fetcher.py`)

Handles all data fetching operations.

**Usage:**

```python
from src.ai_agent.workflow.data_fetcher import MarketDataFetcher

# Initialize fetcher
fetcher = MarketDataFetcher(period='6mo')

# Fetch price data
df = fetcher.fetch_price_data('AAPL')
print(df.head())

# Fetch fundamentals
fundamentals = fetcher.fetch_fundamentals('AAPL')
print(fundamentals)  # {'sector': 'Technology', 'pe': 28.5, ...}

# Format fundamentals
formatted = fetcher.format_fundamentals(fundamentals)
print(formatted)  # "Apple Inc., Sector: Technology, PE: 28.5"
```

### 5. Analysis Nodes (`nodes/`)

Individual analysis steps as modular components.

#### TechnicalAnalysisNode

```python
from src.ai_agent.workflow.nodes import TechnicalAnalysisNode
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-70b-versatile", groq_api_key="...")
node = TechnicalAnalysisNode(llm)

# Process is called automatically by workflow
# state = node.process(state)
```

#### RiskAssessmentNode

```python
from src.ai_agent.workflow.nodes import RiskAssessmentNode

risk_node = RiskAssessmentNode(llm)
# state = risk_node.process(state)
```

#### RecommendationNode

```python
from src.ai_agent.workflow.nodes import RecommendationNode

rec_node = RecommendationNode(llm)
# state = rec_node.process(state)
```

### 6. RAGAnalyzer (`rag_analyzer.py`)

Pattern recognition using historical data and RAG.

**Usage:**

```python
from src.ai_agent.workflow import RAGAnalyzer

# Initialize analyzer
analyzer = RAGAnalyzer()

# Initialize with historical patterns (optional)
patterns = [
    "RSI 70, MACD positive, resulted in 10% gain",
    "RSI 30, MACD negative, resulted in 5% drop"
]
analyzer.initialize_vectorstore(patterns)

# Find similar patterns
similar = analyzer.find_similar_patterns("RSI 65, MACD positive")
print(similar)

# Analyze with context
import pandas as pd
df = pd.read_csv('market_data.csv')
analysis = analyzer.analyze_with_context(df, 'AAPL')
print(analysis)
```

---

## 🔄 Workflow Execution Flow

```
User: workflow.analyze('AAPL')
    ↓
[1] fetch_data_node
    → MarketDataFetcher.fetch_price_data()
    → Download 6mo data, add signals
    → state['market_data'] = DataFrame
    ↓
[2] fundamental_context_node
    → MarketDataFetcher.fetch_fundamentals()
    → Get P/E, sector, market cap
    → state['fundamental_context'] = string
    ↓
[3] technical_analysis (TechnicalAnalysisNode)
    → Extract RSI, MACD, price metrics
    → Build prompt with WorkflowPrompts
    → LLM analysis → parse response
    → state['technical_analysis'] = summary
    → state['technical_structured'] = JSON
    ↓
[4] risk_assessment (RiskAssessmentNode)
    → Calculate volatility, drawdown, ATR
    → Build prompt with risk metrics
    → LLM analysis → parse response
    → state['risk_assessment'] = summary
    → state['risk_structured'] = JSON
    ↓
[5] generate_recommendation (RecommendationNode)
    → Combine technical + risk + fundamentals
    → Build final prompt
    → LLM recommendation → parse response
    → state['final_recommendation'] = summary
    → state['recommendation_structured'] = JSON
    ↓
Return complete state dictionary
```

---

## 🎨 Architecture Benefits

### 1. **Separation of Concerns**

Each component has ONE responsibility:
- `data_fetcher.py` → Fetch data only
- `prompts.py` → Manage prompts only
- `nodes/technical_node.py` → Technical analysis only
- `ta_workflow.py` → Orchestrate workflow only

### 2. **Easy Testing**

Test each component independently:

```python
# Test data fetcher
def test_data_fetcher():
    fetcher = MarketDataFetcher()
    df = fetcher.fetch_price_data('AAPL')
    assert not df.empty
    assert 'Close' in df.columns

# Test technical node
def test_technical_node():
    mock_llm = MockChatGroq()
    node = TechnicalAnalysisNode(mock_llm)
    mock_state = {'ticker': 'AAPL', 'market_data': df, ...}
    result = node.process(mock_state)
    assert 'technical_analysis' in result

# Test prompts
def test_prompts():
    prompt = WorkflowPrompts.get_technical_prompt(
        ticker='AAPL', price=150, rsi=60, ...
    )
    assert 'AAPL' in prompt
    assert '150' in prompt
```

### 3. **Maintainability**

- Update prompts in ONE place (`prompts.py`)
- Fix data fetching without touching analysis
- Add new nodes without modifying existing ones

### 4. **Extensibility**

```python
# Add a new node easily
class SentimentNode:
    def process(self, state):
        # Sentiment analysis logic
        return state

# Add to workflow
workflow.add_node("sentiment", sentiment_node.process)
workflow.add_edge("fundamental_context", "sentiment")
workflow.add_edge("sentiment", "technical_analysis")
```

---

## 📊 Comparison: Before vs After

### Before (Monolithic)

```
langgraph_workflow.py - 403 lines
├── AnalysisState (mixed with code)
├── TAWorkflow
│   ├── _build_workflow
│   ├── fetch_data_node (data fetching + logic)
│   ├── fundamental_context_node (data + formatting)
│   ├── technical_analysis_node (metrics + prompts + LLM + parsing)
│   ├── risk_assessment_node (metrics + prompts + LLM + parsing)
│   └── recommendation_node (prompts + LLM + parsing)
└── RAGAnalyzer (mixed with TAWorkflow)
```

**Issues:**
❌ 403 lines in one file  
❌ Mixed responsibilities  
❌ Prompts hardcoded in methods  
❌ Hard to test individual components  
❌ Difficult to extend

### After (Modular)

```
workflow/ - ~900 lines across 10 files
├── states.py (30 lines)
│   └── AnalysisState, WorkflowConfig
├── prompts.py (150 lines)
│   └── All prompts centralized
├── data_fetcher.py (130 lines)
│   └── MarketDataFetcher
├── nodes/ (400 lines total)
│   ├── technical_node.py (150 lines)
│   ├── risk_node.py (150 lines)
│   └── recommendation_node.py (100 lines)
├── ta_workflow.py (150 lines)
│   └── TAWorkflow orchestrator
└── rag_analyzer.py (130 lines)
    └── RAGAnalyzer
```

**Benefits:**
✅ Clear separation of concerns  
✅ Easy to test each component  
✅ Prompts centralized and maintainable  
✅ Can extend without breaking existing code  
✅ Production-ready structure

---

## 🚀 Usage Examples

### Example 1: Basic Analysis

```python
from src.ai_agent.workflow import TAWorkflow

workflow = TAWorkflow()
result = workflow.analyze('AAPL')

print("=== RECOMMENDATION ===")
print(result['final_recommendation'])

print("\n=== ACTION ===")
print(f"Action: {result['recommendation_structured']['action']}")
print(f"Entry: ${result['recommendation_structured']['entry_price']}")
print(f"Stop Loss: ${result['recommendation_structured']['stop_loss']}")
```

### Example 2: Custom Period

```python
# Analyze with 1 year of data
workflow = TAWorkflow(data_period='1y')
result = workflow.analyze('MSFT')
```

### Example 3: Access Structured Data

```python
result = workflow.analyze('GOOGL')

# Technical signals
tech = result['technical_structured']
print(f"Patterns: {tech['patterns']}")
print(f"Trend: {tech['trend']['direction']} ({tech['trend']['strength']})")
print(f"Support: {tech['support_levels']}")
print(f"Resistance: {tech['resistance_levels']}")

# Risk metrics
risk = result['risk_structured']
print(f"Volatility: {risk['volatility_20d_pct']}%")
print(f"Max Drawdown: {risk['max_drawdown_60d_pct']}%")
print(f"Position Size: {risk['position_sizing_rule']}")
```

### Example 4: Batch Analysis

```python
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
workflow = TAWorkflow()

results = {}
for ticker in tickers:
    try:
        result = workflow.analyze(ticker)
        results[ticker] = {
            'action': result['recommendation_structured']['action'],
            'entry': result['recommendation_structured']['entry_price'],
            'confidence': result['technical_structured'].get('confidence', 0)
        }
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")

# Display results
for ticker, data in results.items():
    print(f"{ticker}: {data['action']} @ ${data['entry']:.2f} (conf: {data['confidence']})")
```

### Example 5: With RAG Pattern Analysis

```python
from src.ai_agent.workflow import TAWorkflow, RAGAnalyzer
import pandas as pd

# Regular analysis
workflow = TAWorkflow()
result = workflow.analyze('TSLA')

# Pattern analysis
rag = RAGAnalyzer()
rag.initialize_vectorstore([
    "High RSI with positive MACD often leads to pullback",
    "Low RSI with negative MACD indicates oversold condition"
])

df = result['market_data']
pattern_analysis = rag.analyze_with_context(df, 'TSLA')

print("=== Standard Analysis ===")
print(result['final_recommendation'])

print("\n=== Pattern Context ===")
print(pattern_analysis)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  # For RAGAnalyzer

# Optional (in config)
DEFAULT_LLM_MODEL=llama-3.1-70b-versatile
LLM_TEMPERATURE=0.7
```

### Custom Configuration

```python
from langchain_groq import ChatGroq
from src.ai_agent.workflow import TAWorkflow
from src.ai_agent.workflow.nodes import TechnicalAnalysisNode

# Custom LLM
custom_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    groq_api_key="your_key"
)

# Build workflow with custom components
workflow = TAWorkflow(data_period='1y')
workflow.technical_node = TechnicalAnalysisNode(custom_llm)
```

---

## 📝 API Reference

### TAWorkflow

**Methods:**
- `__init__(data_period='6mo')` - Initialize workflow
- `analyze(ticker: str) -> dict` - Run complete analysis

### MarketDataFetcher

**Methods:**
- `fetch_price_data(ticker: str) -> pd.DataFrame` - Get price data
- `fetch_fundamentals(ticker: str) -> dict` - Get fundamental data
- `format_fundamentals(fundamentals: dict) -> str` - Format as string

### WorkflowPrompts

**Class Attributes:**
- `TECHNICAL_SYSTEM` - Technical analysis system prompt
- `RISK_SYSTEM` - Risk assessment system prompt
- `RECOMMENDATION_SYSTEM` - Recommendation system prompt

**Static Methods:**
- `get_technical_prompt(...)` - Build technical prompt
- `get_risk_prompt(...)` - Build risk prompt
- `get_recommendation_prompt(...)` - Build recommendation prompt

### Analysis Nodes

**All nodes have:**
- `__init__(llm: ChatGroq)` - Initialize with LLM
- `process(state: AnalysisState) -> AnalysisState` - Process node

---

## 🔍 Troubleshooting

### Issue: Import Error

**Problem:**
```python
ImportError: cannot import name 'TAWorkflow' from 'src.ai_agent.workflow'
```

**Solution:**
Make sure you're importing from the new location:
```python
# Old (deprecated)
from src.ai_agent.langgraph_workflow import TAWorkflow

# New (correct)
from src.ai_agent.workflow import TAWorkflow
```

### Issue: No Data Returned

**Problem:**
```
ValueError: No data returned for TICKER
```

**Solution:**
- Check ticker symbol is valid
- Ensure internet connection
- Try longer data period

### Issue: LLM Response Parsing Failed

**Problem:**
```
Warning: Failed to parse structured output
```

**Solution:**
- This is non-critical - human-readable output still works
- Structured output may be empty but analysis continues
- Check LLM is returning valid JSON

---

## 📚 Related Documentation

- [Agents Module](../agents/README.md) - TA Agent and Portfolio Agent
- [RAG Module](../rag/README.md) - RAG document analysis
- [Architecture Guide](../../../../documents/ARCHITECTURE_V2.md) - System architecture
- [Workflow Restructure Plan](../../../../documents/WORKFLOW_RESTRUCTURE_PLAN.md) - Detailed refactoring info

---

## ✨ Summary

**Workflow Module provides:**
- ✅ 5-step LangGraph analysis pipeline
- ✅ Modular, testable components
- ✅ Centralized prompt management
- ✅ Structured + human-readable outputs
- ✅ Easy to extend and customize
- ✅ Production-ready architecture

**Perfect for:**
- Comprehensive stock analysis
- Multi-step AI workflows
- Pattern recognition
- Risk-aware recommendations

---

**Version:** 2.0  
**Last Updated:** January 2026  
**Status:** Production Ready
