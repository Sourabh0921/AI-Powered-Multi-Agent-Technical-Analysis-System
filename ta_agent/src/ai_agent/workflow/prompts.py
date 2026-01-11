# workflow/prompts.py
"""
Centralized prompts for workflow nodes
"""
import json
from typing import Dict, Any


class WorkflowPrompts:
    """Centralized prompts for workflow nodes"""
    
    # ==================== SYSTEM PROMPTS ====================
    
    TECHNICAL_SYSTEM = "You are a technical analysis expert. Be precise, avoid speculation."
    
    RISK_SYSTEM = "You are a risk management specialist. Provide practical, conservative guidance."
    
    RECOMMENDATION_SYSTEM = "You are a senior market strategist providing actionable, risk-aware recommendations."
    
    # ==================== JSON SCHEMAS ====================
    
    TECHNICAL_JSON_SCHEMA = {
        "patterns": ["string"],
        "trend": {"direction": "up|down|sideways", "strength": "low|medium|high"},
        "support_levels": ["number"],
        "resistance_levels": ["number"],
        "signals": {"bullish": ["string"], "bearish": ["string"]},
        "confidence": "0.0-1.0"
    }
    
    RISK_JSON_SCHEMA = {
        "volatility_20d_pct": "number",
        "max_drawdown_60d_pct": "number",
        "atr_14": "number",
        "position_sizing_rule": "string",
        "stop_loss_rule": "string",
        "risk_notes": ["string"],
    }
    
    RECOMMENDATION_JSON_SCHEMA = {
        "action": "BUY|SELL|HOLD",
        "entry_price": "number",
        "stop_loss": "number",
        "take_profit": ["number"],
        "position_size_pct": "number",
        "time_horizon_days": "integer",
        "narrative": "string"
    }
    
    # ==================== PROMPT TEMPLATES ====================
    
    @staticmethod
    def get_technical_prompt(
        ticker: str,
        price: float,
        rsi: float,
        macd: float,
        signal: str,
        trend_20d: float,
        fundamentals: str
    ) -> str:
        """
        Build technical analysis prompt
        
        Args:
            ticker: Stock ticker
            price: Current price
            rsi: RSI value
            macd: MACD value
            signal: Signal indicator
            trend_20d: 20-day trend percentage
            fundamentals: Fundamental context string
            
        Returns:
            Formatted prompt string
        """
        return f"""Analyze {ticker} with a concise focus on price action, patterns, and levels.

Latest metrics:
- Price: ${price:.2f}
- RSI: {rsi:.2f}
- MACD: {macd:.4f}
- Signal: {signal}

20-day trend: {trend_20d:.2f}%
Fundamentals (quick): {fundamentals}

Return TWO parts: 
1) A 4-6 sentence human-readable summary.
2) A pure JSON object only (no markdown) matching this schema: {json.dumps(WorkflowPrompts.TECHNICAL_JSON_SCHEMA)}"""
    
    @staticmethod
    def get_risk_prompt(
        ticker: str,
        volatility_20d: float,
        max_drawdown: float,
        atr_14: Any,
        technical_summary: str
    ) -> str:
        """
        Build risk assessment prompt
        
        Args:
            ticker: Stock ticker
            volatility_20d: 20-day volatility percentage
            max_drawdown: Maximum drawdown percentage
            atr_14: ATR(14) value
            technical_summary: Technical analysis summary
            
        Returns:
            Formatted prompt string
        """
        return f"""Risk assessment for {ticker}:

Volatility (20d): {volatility_20d:.2f}%
Max Drawdown (60d): {max_drawdown:.2f}%
ATR(14): {atr_14}

Technical analysis summary:
{technical_summary}

Return TWO parts: 
1) A concise human-readable risk summary (3-5 sentences).
2) A pure JSON object only (no markdown) with this schema: {json.dumps(WorkflowPrompts.RISK_JSON_SCHEMA)}"""
    
    @staticmethod
    def get_recommendation_prompt(
        ticker: str,
        technical_summary: str,
        risk_summary: str,
        fundamentals: str
    ) -> str:
        """
        Build final recommendation prompt
        
        Args:
            ticker: Stock ticker
            technical_summary: Technical analysis summary
            risk_summary: Risk assessment summary
            fundamentals: Fundamental context string
            
        Returns:
            Formatted prompt string
        """
        return f"""Create final recommendation for {ticker} given the following context.

TECHNICAL ANALYSIS (summary):
{technical_summary}

RISK ASSESSMENT (summary):
{risk_summary}

FUNDAMENTALS (quick): {fundamentals}

Return TWO parts: 
1) A crisp human-readable action plan (3-6 sentences).
2) A pure JSON object only (no markdown) matching this schema: {json.dumps(WorkflowPrompts.RECOMMENDATION_JSON_SCHEMA)}"""
