"""
LLM Market Analyzer
Uses LLM to analyze technical indicators and provide market insights
"""
from typing import Dict
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from ...core.config import settings
from .prompts import (
    MARKET_ANALYSIS_PROMPT,
    MARKET_ANALYSIS_TEMPLATE,
    TRADING_STRATEGY_SYSTEM,
    TRADING_STRATEGY_TEMPLATE,
    INDICATOR_EXPLANATION_SYSTEM,
    INDICATOR_EXPLANATION_TEMPLATE
)


class LLMMarketAnalyzer:
    """
    AI-powered market analysis using LangChain and Groq LLM
    
    Provides:
    - Technical indicator analysis
    - Trading strategy generation
    - Indicator explanations
    """
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.3):
        """
        Initialize LLM market analyzer
        
        Args:
            model: Groq model name
            temperature: LLM temperature (0-1)
        """
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
        self.model = model
        self.temperature = temperature
    
    def analyze_market_data(self, df: pd.DataFrame, ticker: str) -> str:
        """
        Analyze market data with technical indicators and provide insights
        
        Args:
            df: DataFrame with OHLCV data and calculated indicators
            ticker: Stock ticker symbol
            
        Returns:
            Comprehensive market analysis
        """
        # Get latest data
        latest = df.iloc[-1]
        recent = df.tail(5)
        
        # Calculate additional context
        price_change = ((latest['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close']) * 100
        volatility = df['close'].pct_change().tail(20).std() * 100
        
        # Determine signal
        signal_value = latest.get('signal', 0)
        if signal_value == 1:
            signal = "BUY"
        elif signal_value == -1:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # Build prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", MARKET_ANALYSIS_PROMPT),
            ("human", MARKET_ANALYSIS_TEMPLATE)
        ])
        
        # Generate analysis
        chain = prompt | self.llm
        
        response = chain.invoke({
            "ticker": ticker,
            "price": latest['close'],
            "change": price_change,
            "vol": volatility,
            "rsi": latest.get('rsi', 0),
            "macd": latest.get('macd', 0),
            "macd_signal": latest.get('macd_signal', 0),
            "signal": signal,
            "recent_data": recent[['close', 'rsi', 'macd']].to_string()
        })
        
        return response.content
    
    def generate_trading_strategy(
        self,
        analysis: str,
        risk_tolerance: str = "moderate"
    ) -> str:
        """
        Generate a trading strategy based on analysis
        
        Args:
            analysis: Market analysis text
            risk_tolerance: Risk tolerance level (conservative, moderate, aggressive)
            
        Returns:
            Trading strategy with entry/exit points
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", TRADING_STRATEGY_SYSTEM),
            ("human", TRADING_STRATEGY_TEMPLATE)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "analysis": analysis,
            "risk_tolerance": risk_tolerance
        })
        
        return response.content
    
    def explain_indicators(self, indicator_data: Dict[str, float]) -> str:
        """
        Explain technical indicator values in simple terms
        
        Args:
            indicator_data: Dictionary of indicator names and values
            
        Returns:
            Simple explanations of each indicator
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", INDICATOR_EXPLANATION_SYSTEM),
            ("human", INDICATOR_EXPLANATION_TEMPLATE)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "indicators": "\n".join([f"- {k}: {v:.2f}" for k, v in indicator_data.items()])
        })
        
        return response.content
