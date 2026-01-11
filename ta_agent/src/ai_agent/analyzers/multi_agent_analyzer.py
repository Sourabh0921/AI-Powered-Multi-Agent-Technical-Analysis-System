"""
Multi-Agent Analyzer
Uses multiple specialized AI agents for comprehensive analysis
"""
from typing import Dict
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from ...core.config import settings
from .agents import TechnicalAgent, SentimentAgent, RiskAgent
from .prompts import SYNTHESIS_SYSTEM, SYNTHESIS_TEMPLATE


class MultiAgentAnalyzer:
    """
    Multi-agent system for comprehensive market analysis
    
    Uses specialized agents:
    - Technical Agent: Chart patterns and indicators
    - Sentiment Agent: Market momentum and psychology
    - Risk Agent: Risk assessment and protective measures
    
    Synthesizes insights into unified recommendations
    """
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.3):
        """
        Initialize multi-agent analyzer
        
        Args:
            model: Groq model name for all agents
            temperature: LLM temperature (0-1)
        """
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
        
        # Initialize specialized agents
        self.technical_agent = TechnicalAgent(model, temperature)
        self.sentiment_agent = SentimentAgent(model, temperature)
        self.risk_agent = RiskAgent(model, temperature)
    
    def analyze(self, df: pd.DataFrame, ticker: str = None) -> Dict[str, str]:
        """
        Run comprehensive multi-agent analysis
        
        Args:
            df: DataFrame with OHLCV data and indicators
            ticker: Optional ticker symbol for context
            
        Returns:
            Dictionary with individual agent insights and synthesis
        """
        # Get insights from each agent
        technical_insights = self.technical_agent.analyze(df)
        sentiment_insights = self.sentiment_agent.analyze(df)
        risk_insights = self.risk_agent.analyze(df)
        
        # Synthesize all insights
        synthesis = self.synthesize_insights(
            technical_insights,
            sentiment_insights,
            risk_insights
        )
        
        return {
            "technical": technical_insights,
            "sentiment": sentiment_insights,
            "risk": risk_insights,
            "synthesis": synthesis,
            "ticker": ticker
        }
    
    def synthesize_insights(
        self,
        technical: str,
        sentiment: str,
        risk: str
    ) -> str:
        """
        Combine insights from all agents into unified recommendation
        
        Args:
            technical: Technical agent insights
            sentiment: Sentiment agent insights
            risk: Risk agent insights
            
        Returns:
            Synthesized recommendation with action items
        """
        messages = [
            SystemMessage(content=SYNTHESIS_SYSTEM),
            HumanMessage(content=SYNTHESIS_TEMPLATE.format(
                technical=technical,
                sentiment=sentiment,
                risk=risk
            ))
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def get_agent_consensus(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Get consensus view from all agents
        
        Args:
            df: DataFrame with market data
            
        Returns:
            Consensus analysis with agreement levels
        """
        analysis = self.analyze(df)
        
        # Simple consensus detection (can be enhanced)
        bullish_count = sum([
            "bullish" in analysis["technical"].lower(),
            "bullish" in analysis["sentiment"].lower(),
            "low risk" in analysis["risk"].lower()
        ])
        
        bearish_count = sum([
            "bearish" in analysis["technical"].lower(),
            "bearish" in analysis["sentiment"].lower(),
            "high risk" in analysis["risk"].lower()
        ])
        
        if bullish_count > bearish_count:
            consensus = "BULLISH"
            confidence = bullish_count / 3
        elif bearish_count > bullish_count:
            consensus = "BEARISH"
            confidence = bearish_count / 3
        else:
            consensus = "NEUTRAL"
            confidence = 0.5
        
        return {
            **analysis,
            "consensus": consensus,
            "confidence": round(confidence * 100, 1),
            "agreement": {
                "bullish_signals": bullish_count,
                "bearish_signals": bearish_count
            }
        }
