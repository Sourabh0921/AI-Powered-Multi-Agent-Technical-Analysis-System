# Agents Module Documentation

Modular architecture for autonomous trading agents with multi-market support.

## 📁 Module Structure

```
agents/
├── __init__.py              # Package exports
├── market_info.py           # Market detection & info (200+ lines)
├── utils.py                 # Helper utilities (150+ lines)
├── prompts.py              # Agent prompts (200+ lines)
├── ta_agent.py             # Technical Analysis Agent (300+ lines)
├── portfolio_agent.py      # Portfolio Analysis Agent (250+ lines)
└── README.md               # This file
```

## 🎯 Core Components

### 1. AutonomousTAAgent (`ta_agent.py`)

Main technical analysis agent for individual stock analysis.

**Key Features:**
- Multi-market support (US, India, UK, Japan, Canada)
- Automatic ticker format detection (.NS, .BO, .L, .T, .TO)
- Batch analysis capabilities
- Quick signal generation
- Comparative analysis

**Usage:**

```python
from ai_agent.agents import AutonomousTAAgent

# Initialize agent
agent = AutonomousTAAgent()

# Single stock analysis
result = agent.analyze("Should I buy AAPL?")

# Batch analysis
results = agent.batch_analyze(
    tickers=['AAPL', 'RELIANCE.NS', 'MSFT'],
    analysis_type='comprehensive'  # or 'quick', 'signals_only'
)

# Compare stocks
comparison = agent.compare_stocks(['AAPL', 'MSFT', 'GOOGL'])

# Get quick signal
signal = agent.get_signal('AAPL')
# Returns: {'ticker': 'AAPL', 'signal': 'BUY', 'analysis': '...'}
```

**Analysis Types:**
- `comprehensive`: Full technical analysis with entry/exit levels
- `quick`: Brief overview with key metrics
- `signals_only`: Just buy/sell/hold recommendation

### 2. PortfolioAnalysisAgent (`portfolio_agent.py`)

Specialized agent for portfolio-level analysis and optimization.

**Key Features:**
- Multi-market portfolio support
- Currency risk analysis
- Diversification scoring
- Rebalancing recommendations
- Risk-adjusted analysis

**Usage:**

```python
from ai_agent.agents import PortfolioAnalysisAgent

# Initialize agent
agent = PortfolioAnalysisAgent()

# Portfolio analysis
analysis = agent.analyze_portfolio(
    tickers=['AAPL', 'RELIANCE.NS', 'MSFT', 'TCS.NS'],
    weights={
        'AAPL': 0.3,
        'RELIANCE.NS': 0.25,
        'MSFT': 0.25,
        'TCS.NS': 0.2
    },
    base_currency='USD'
)

# Diversification score
div_score = agent.get_diversification_score(
    tickers=['AAPL', 'RELIANCE.NS'],
    weights={'AAPL': 0.5, 'RELIANCE.NS': 0.5}
)
# Returns:
# {
#   'diversification_score': 50.0,
#   'market_diversification_score': 50.0,
#   'concentration_risk': 'Low',
#   'num_holdings': 2,
#   'num_markets': 2
# }

# Rebalancing suggestions
rebalance = agent.suggest_rebalancing(
    tickers=['AAPL', 'MSFT'],
    current_weights={'AAPL': 0.7, 'MSFT': 0.3},
    target_allocation={'AAPL': 0.5, 'MSFT': 0.5}
)

# Currency risk
currency_risk = agent.analyze_currency_risk(
    tickers=['AAPL', 'RELIANCE.NS'],
    weights={'AAPL': 0.6, 'RELIANCE.NS': 0.4},
    base_currency='USD'
)
```

### 3. MarketDetector (`market_info.py`)

Intelligent market detection from ticker symbols.

**Supported Markets:**
- 🇺🇸 **US**: NASDAQ, NYSE (no suffix)
- 🇮🇳 **NSE**: National Stock Exchange (.NS)
- 🇮🇳 **BSE**: Bombay Stock Exchange (.BO)
- 🇬🇧 **LSE**: London Stock Exchange (.L)
- 🇯🇵 **TSE**: Tokyo Stock Exchange (.T)
- 🇨🇦 **TSX**: Toronto Stock Exchange (.TO)

**Usage:**

```python
from ai_agent.agents import MarketDetector, MarketInfo

detector = MarketDetector()

# Detect market
market = detector.detect_market('RELIANCE.NS')  # Returns: 'NSE'
market = detector.detect_market('AAPL')         # Returns: 'US'

# Get market info
info = detector.get_market_info('RELIANCE.NS')
# Returns:
# {
#   'name': 'National Stock Exchange of India',
#   'currency': 'INR',
#   'timezone': 'Asia/Kolkata',
#   'trading_hours': '9:15 AM - 3:30 PM IST',
#   'characteristics': 'Large-cap focused, high liquidity'
# }

# Get market context (for prompts)
context = detector.get_market_context('RELIANCE.NS')

# Check if Indian market
is_indian = detector.is_indian_market('RELIANCE.NS')  # True

# Batch detection
markets = detector.batch_detect_markets([
    'AAPL', 'RELIANCE.NS', 'MSFT', 'TCS.BO'
])
# Returns: {'AAPL': 'US', 'RELIANCE.NS': 'NSE', ...}
```

### 4. TickerExtractor (`utils.py`)

Extract and validate ticker symbols from text.

**Usage:**

```python
from ai_agent.agents import TickerExtractor

extractor = TickerExtractor()

# Extract tickers from query
tickers = extractor.extract_tickers(
    "Should I buy AAPL, RELIANCE.NS, and MSFT?"
)
# Returns: ['AAPL', 'RELIANCE.NS', 'MSFT']

# Validate ticker format
is_valid = extractor.validate_ticker_format('AAPL')  # True
is_valid = extractor.validate_ticker_format('123')   # False

# Normalize ticker
normalized = extractor.normalize_ticker(' aapl ')  # 'AAPL'

# Split ticker and suffix
symbol, suffix = extractor.split_ticker_and_suffix('RELIANCE.NS')
# Returns: ('RELIANCE', '.NS')
```

### 5. TextFormatter (`utils.py`)

Format financial data for display.

**Usage:**

```python
from ai_agent.agents import TextFormatter

formatter = TextFormatter()

# Format price
price_str = formatter.format_price(1234.56, 'USD')
# Returns: "$1,234.56"

price_str = formatter.format_price(10500.75, 'INR')
# Returns: "₹10,500.75"

# Format percentage
pct_str = formatter.format_percentage(0.0525)
# Returns: "+5.25%"

pct_str = formatter.format_percentage(-0.032)
# Returns: "-3.20%"

# Create section header
header = formatter.create_section_header("Portfolio Analysis")
# Returns formatted markdown header
```

### 6. WeightValidator (`utils.py`)

Validate and normalize portfolio weights.

**Usage:**

```python
from ai_agent.agents import WeightValidator

validator = WeightValidator()

# Validate weights
weights = {'AAPL': 0.5, 'MSFT': 0.5}
is_valid = validator.validate_weights(weights)  # True

weights = {'AAPL': 0.6, 'MSFT': 0.5}
is_valid = validator.validate_weights(weights)  # False (sum > 1)

# Normalize weights
weights = {'AAPL': 0.6, 'MSFT': 0.6}
normalized = validator.normalize_weights(weights)
# Returns: {'AAPL': 0.5, 'MSFT': 0.5}

# Create equal weights
tickers = ['AAPL', 'MSFT', 'GOOGL']
equal_weights = validator.create_equal_weights(tickers)
# Returns: {'AAPL': 0.333, 'MSFT': 0.333, 'GOOGL': 0.333}
```

### 7. AgentPrompts (`prompts.py`)

Centralized prompt management.

**Usage:**

```python
from ai_agent.agents import AgentPrompts

# Get TA system prompt (with optional market context)
system_prompt = AgentPrompts.get_ta_system_prompt(
    market_context="Analyzing Indian NSE stocks"
)

# Get portfolio system prompt
portfolio_prompt = AgentPrompts.get_portfolio_system_prompt()

# Query templates
query = AgentPrompts.get_comprehensive_analysis_query(
    ticker='AAPL',
    market_name='US Stock Market',
    currency='USD'
)

quick_query = AgentPrompts.get_quick_analysis_query('AAPL', 'USD')
signals_query = AgentPrompts.get_signals_query('AAPL', 'USD')
comparison_query = AgentPrompts.get_comparison_query(
    ['AAPL', 'MSFT'],
    ['US', 'US']
)
```

## 🔄 Integration Examples

### Example 1: Multi-Market Portfolio Analysis

```python
from ai_agent.agents import PortfolioAnalysisAgent

agent = PortfolioAnalysisAgent()

# Analyze global portfolio
analysis = agent.analyze_portfolio(
    tickers=[
        'AAPL',        # US
        'RELIANCE.NS', # India NSE
        'TCS.BO',      # India BSE
        'BP.L',        # UK
        'SONY.T'       # Japan
    ],
    weights={
        'AAPL': 0.3,
        'RELIANCE.NS': 0.25,
        'TCS.BO': 0.15,
        'BP.L': 0.2,
        'SONY.T': 0.1
    },
    base_currency='USD'
)

print(analysis)
```

### Example 2: Market-Aware Batch Analysis

```python
from ai_agent.agents import AutonomousTAAgent

agent = AutonomousTAAgent()

# Analyze stocks from different markets
results = agent.batch_analyze(
    tickers=[
        'AAPL',        # US
        'RELIANCE.NS', # India
        'MSFT',        # US
        'TCS.NS',      # India
        'GOOGL'        # US
    ],
    analysis_type='comprehensive'
)

for ticker, result in results.items():
    print(f"\n{ticker} ({result['market']} - {result['currency']}):")
    print(result['analysis'])
```

### Example 3: Diversification Analysis

```python
from ai_agent.agents import PortfolioAnalysisAgent

agent = PortfolioAnalysisAgent()

# Check portfolio diversification
score = agent.get_diversification_score(
    tickers=['AAPL', 'RELIANCE.NS', 'MSFT', 'TCS.NS'],
    weights={
        'AAPL': 0.4,
        'RELIANCE.NS': 0.3,
        'MSFT': 0.2,
        'TCS.NS': 0.1
    }
)

print(f"Diversification Score: {score['diversification_score']}/100")
print(f"Market Diversification: {score['market_diversification_score']}/100")
print(f"Concentration Risk: {score['concentration_risk']}")
print(f"Markets: {score['num_markets']}")
```

## 🏗️ Architecture

### Module Dependencies

```
ta_agent.py
    ├── market_info.py (MarketDetector, MarketInfo)
    ├── utils.py (TickerExtractor)
    └── prompts.py (AgentPrompts)

portfolio_agent.py
    ├── ta_agent.py (AutonomousTAAgent)
    ├── market_info.py (MarketDetector)
    ├── utils.py (WeightValidator)
    └── prompts.py (AgentPrompts)

market_info.py (standalone)
utils.py (standalone)
prompts.py (standalone)
```

### Data Flow

```
User Query
    ↓
AutonomousTAAgent.analyze()
    ↓
TickerExtractor.extract_tickers() → Extract tickers
    ↓
MarketDetector.get_market_context() → Get market info
    ↓
AgentPrompts.get_ta_system_prompt() → Build prompt
    ↓
LLM.invoke() → Generate analysis
    ↓
Response
```

## 🔧 Configuration

### Environment Variables

```python
# Required
GROQ_API_KEY=your_groq_api_key

# Optional
LLM_MODEL=openai/gpt-oss-120b  # Default model
LLM_TEMPERATURE=0.7             # Default temperature
```

### Model Selection

```python
# Use different models
ta_agent = AutonomousTAAgent(
    model="openai/gpt-oss-120b",    # Default
    temperature=0.7
)

portfolio_agent = PortfolioAnalysisAgent(
    model="openai/gpt-oss-120b",
    temperature=0.3                  # Lower for consistency
)
```

## 📊 Market Coverage

| Market | Suffix | Currency | Example |
|--------|--------|----------|---------|
| US (NASDAQ/NYSE) | None | USD | AAPL |
| India NSE | .NS | INR | RELIANCE.NS |
| India BSE | .BO | INR | TATA.BO |
| UK LSE | .L | GBP | BP.L |
| Japan TSE | .T | JPY | SONY.T |
| Canada TSX | .TO | CAD | RY.TO |

## 🚀 Quick Start

### Basic TA Analysis

```python
from ai_agent.agents import AutonomousTAAgent

agent = AutonomousTAAgent()
result = agent.analyze("Analyze AAPL with entry and exit levels")
print(result)
```

### Portfolio Analysis

```python
from ai_agent.agents import PortfolioAnalysisAgent

agent = PortfolioAnalysisAgent()
result = agent.analyze_portfolio(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    base_currency='USD'
)
print(result)
```

## 🛠️ Extending the Module

### Adding New Markets

1. Update `market_info.py` → `MarketInfo.MARKET_DATA`
2. Add suffix pattern to `MarketDetector.detect_market()`
3. Update documentation

### Creating Custom Prompts

```python
# In your code
from ai_agent.agents import AgentPrompts

# Use existing prompts as templates
custom_prompt = AgentPrompts.get_comprehensive_analysis_query(
    ticker='CUSTOM',
    market_name='Custom Market',
    currency='USD'
)

# Or create your own
custom_prompt = f"""
{AgentPrompts.TA_AGENT_SYSTEM}

Additional instructions: ...
"""
```

## 📝 Best Practices

1. **Always validate weights** before portfolio analysis
2. **Use batch_analyze** for multiple tickers (more efficient)
3. **Include market context** for accurate analysis
4. **Lower temperature** (0.3-0.5) for portfolio analysis
5. **Higher temperature** (0.7-0.9) for creative analysis

## 🔍 Troubleshooting

### Issue: Ticker not recognized
**Solution:** Check ticker format matches market suffix

### Issue: Weights don't sum to 1.0
**Solution:** Use `WeightValidator.normalize_weights()`

### Issue: Market context missing
**Solution:** Ensure `include_market_context=True` in analyze()

## 📚 Related Documentation

- [RAG Integration Guide](../../RAG_AGENT_INTEGRATION_EXPLAINED.md)
- [API Documentation](../../api/README.md)
- [Complete Architecture](../../documents/ARCHITECTURE_V2.md)

---

**Version:** 2.0  
**Last Updated:** 2024  
**Maintainer:** TA Agent Team
