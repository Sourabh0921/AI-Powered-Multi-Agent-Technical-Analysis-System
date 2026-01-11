"""
Individual specialized agents for multi-agent analysis
"""
from typing import Dict
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from ...core.config import settings
from .prompts import (
    TECHNICAL_AGENT_SYSTEM,
    TECHNICAL_AGENT_TEMPLATE,
    SENTIMENT_AGENT_SYSTEM,
    SENTIMENT_AGENT_TEMPLATE,
    RISK_AGENT_SYSTEM,
    RISK_AGENT_TEMPLATE
)


class TechnicalAgent:
    """Agent specialized in technical analysis"""
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.3):
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
    
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Analyze technical indicators and chart patterns
        
        Args:
            df: DataFrame with OHLCV data and indicators
            
        Returns:
            Technical analysis insights
        """
        latest = df.iloc[-1]
        
        messages = [
            SystemMessage(content=TECHNICAL_AGENT_SYSTEM),
            HumanMessage(content=TECHNICAL_AGENT_TEMPLATE.format(
                rsi=latest.get('rsi', 0),
                macd=latest.get('macd', 0),
                price=latest['close'],
                volume=latest.get('volume', 0)
            ))
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class SentimentAgent:
    """Agent specialized in market sentiment analysis"""
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.3):
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
    
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Analyze market sentiment and momentum
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Sentiment analysis insights
        """
        price_trend = "uptrend" if df['close'].iloc[-1] > df['close'].iloc[-20] else "downtrend"
        volatility = df['close'].pct_change().tail(10).std() * 100
        
        messages = [
            SystemMessage(content=SENTIMENT_AGENT_SYSTEM),
            HumanMessage(content=SENTIMENT_AGENT_TEMPLATE.format(
                trend=price_trend,
                volatility=volatility
            ))
        ]
        
        response = self.llm.invoke(messages)
        return response.content


class RiskAgent:
    """Agent specialized in risk assessment"""
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.3):
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
    
    def analyze(self, df: pd.DataFrame) -> str:
        """
        Assess risk factors and volatility
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Risk assessment insights
        """
        volatility = df['close'].pct_change().tail(20).std() * 100
        min_price = df['close'].tail(20).min()
        max_price = df['close'].tail(20).max()
        
        messages = [
            SystemMessage(content=RISK_AGENT_SYSTEM),
            HumanMessage(content=RISK_AGENT_TEMPLATE.format(
                volatility=volatility,
                min_price=min_price,
                max_price=max_price
            ))
        ]
        
        response = self.llm.invoke(messages)
        return response.content
