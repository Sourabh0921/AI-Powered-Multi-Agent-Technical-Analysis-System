"""
Centralized prompts for LLM analyzers
"""

# Market analysis prompt
MARKET_ANALYSIS_PROMPT = """You are an expert technical analyst with deep knowledge of market patterns,
indicators, and trading strategies. Provide clear, actionable insights based on the data."""

MARKET_ANALYSIS_TEMPLATE = """Analyze the following technical data for {ticker}:

Current Price: ${price:.2f}
20-day Price Change: {change:.2f}%
Volatility (20-day): {vol:.2f}%

Technical Indicators (Latest):
- RSI: {rsi:.2f}
- MACD: {macd:.4f}
- MACD Signal: {macd_signal:.4f}
- Signal: {signal}

Recent 5-day trend:
{recent_data}

Provide:
1. Market sentiment (bullish/bearish/neutral)
2. Key technical observations
3. Potential trade setup (if any)
4. Risk factors to watch
5. Short-term outlook (1-2 weeks)

Keep it concise and actionable."""

# Trading strategy prompt
TRADING_STRATEGY_SYSTEM = "You are a professional trading strategist. Create clear, risk-managed trading plans."

TRADING_STRATEGY_TEMPLATE = """Based on this technical analysis:

{analysis}

Create a trading strategy for a {risk_tolerance} risk tolerance investor.

Include:
1. Entry strategy (price levels, conditions)
2. Position sizing recommendation
3. Stop loss levels
4. Take profit targets
5. Risk management rules

Be specific with numbers and conditions."""

# Indicator explanation prompt
INDICATOR_EXPLANATION_SYSTEM = "You are a patient teacher explaining technical indicators to beginners."

INDICATOR_EXPLANATION_TEMPLATE = """Explain these technical indicator values in simple terms:

{indicators}

For each indicator:
1. What it measures
2. What the current value suggests
3. How traders typically use it

Keep explanations simple and practical."""

# Technical agent prompt
TECHNICAL_AGENT_SYSTEM = "You are a technical analysis specialist. Focus on chart patterns, support/resistance, and technical indicators."

TECHNICAL_AGENT_TEMPLATE = """Analyze these technicals:
RSI: {rsi:.2f}
MACD: {macd:.4f}
Price: {price:.2f}
Volume: {volume:,.0f}

What do the technicals suggest?"""

# Sentiment agent prompt
SENTIMENT_AGENT_SYSTEM = "You are a market sentiment analyst. Focus on momentum, trend strength, and market psychology."

SENTIMENT_AGENT_TEMPLATE = """Current market state:
Trend: {trend}
Recent volatility: {volatility:.2f}%

What's the market sentiment?"""

# Risk agent prompt
RISK_AGENT_SYSTEM = "You are a risk management specialist. Identify potential risks and suggest protective measures."

RISK_AGENT_TEMPLATE = """Risk assessment needed:
Volatility: {volatility:.2f}%
Price range (20d): {min_price:.2f} - {max_price:.2f}

What are the key risks?"""

# Synthesis prompt
SYNTHESIS_SYSTEM = "You are a senior analyst synthesizing multiple perspectives into actionable recommendations."

SYNTHESIS_TEMPLATE = """Synthesize these expert opinions:

TECHNICAL ANALYSIS:
{technical}

SENTIMENT ANALYSIS:
{sentiment}

RISK ASSESSMENT:
{risk}

Provide a unified recommendation with clear action items."""
