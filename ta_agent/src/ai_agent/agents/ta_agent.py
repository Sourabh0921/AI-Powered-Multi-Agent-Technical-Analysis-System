# agents/ta_agent.py
"""
Autonomous Technical Analysis Agent
Main agent for market analysis and trading recommendations
"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional, Dict, List
from datetime import datetime
import logging

from ...core.config import settings
from .market_info import MarketDetector, MarketInfo
from .utils import TickerExtractor
from .prompts import AgentPrompts

logger = logging.getLogger(__name__)


class AutonomousTAAgent:
    """
    Autonomous Technical Analysis Agent
    
    Capabilities:
    - Analyze stocks from multiple markets (US, India, Global)
    - Provide trading recommendations with market-specific context
    - Handle different ticker formats (.NS, .BO, .L, .TO, etc.)
    - Multi-timeframe analysis
    - Risk management suggestions
    
    Usage:
        agent = AutonomousTAAgent()
        result = agent.analyze("Should I buy AAPL?")
        batch_results = agent.batch_analyze(["AAPL", "RELIANCE.NS", "MSFT"])
    """
    
    def __init__(self, model: str = "openai/gpt-oss-120b", temperature: float = 0.7):
        """
        Initialize TA Agent
        
        Args:
            model: LLM model to use
            temperature: LLM temperature (0.0-1.0)
        """
        self.llm = ChatGroq(
            model=model,
            temperature=temperature,
            groq_api_key=settings.GROQ_API_KEY
        )
        self.market_detector = MarketDetector()
        self.ticker_extractor = TickerExtractor()
        
        logger.info(f"AutonomousTAAgent initialized with model: {model}")
    
    def analyze(
        self, 
        query: str, 
        chat_history: list = None, 
        include_market_context: bool = True
    ) -> str:
        """
        Analyze based on user query with enhanced multi-market support
        
        Examples:
        - "Analyze AAPL, RELIANCE.NS, TCS.NS, WIPRO.NS, JIOFIN.NS stock"
        - "Should I buy TSLA, RELIANCE.NS?"
        - "What are the technical indicators for MSFT, INFY.NS?"
        - "Compare HDFC BANK.NS with JPM"
        
        Args:
            query: User's analysis query
            chat_history: Optional conversation history
            include_market_context: Whether to add market-specific context
            
        Returns:
            Analysis response string
        """
        # Extract tickers from query if present
        tickers = self.ticker_extractor.extract_tickers(query)
        market_context = ""
        
        if include_market_context and tickers:
            market_contexts = [
                self.market_detector.get_market_context(ticker) 
                for ticker in tickers
            ]
            market_context = "\n".join(market_contexts)
        
        # Build system prompt
        system_prompt = AgentPrompts.get_ta_system_prompt(market_context)
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)
        
        # Add user query
        messages.append(HumanMessage(content=query))
        
        # Get LLM response
        logger.info(f"Analyzing query with {len(tickers)} tickers detected")
        response = self.llm.invoke(messages)
        
        return response.content
    
    def batch_analyze(
        self, 
        tickers: List[str], 
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Dict]:
        """
        Analyze multiple tickers with market-aware prompts
        
        Args:
            tickers: List of ticker symbols
            analysis_type: Type of analysis
                - 'comprehensive': Full technical analysis
                - 'quick': Brief overview
                - 'signals_only': Just buy/sell/hold signal
                
        Returns:
            Dictionary mapping ticker to analysis results
        """
        results = {}
        
        logger.info(f"Batch analyzing {len(tickers)} tickers, type: {analysis_type}")
        
        for ticker in tickers:
            try:
                # Get market info
                market = self.market_detector.detect_market(ticker)
                market_info = MarketInfo.get_market_info(market)
                
                # Build query based on analysis type
                if analysis_type == "comprehensive":
                    query = AgentPrompts.get_comprehensive_analysis_query(
                        ticker=ticker,
                        market_name=market_info['name'],
                        currency=market_info['currency']
                    )
                elif analysis_type == "quick":
                    query = AgentPrompts.get_quick_analysis_query(
                        ticker=ticker,
                        currency=market_info['currency']
                    )
                else:  # signals_only
                    query = AgentPrompts.get_signals_query(
                        ticker=ticker,
                        currency=market_info['currency']
                    )
                
                # Analyze
                analysis = self.analyze(query, include_market_context=True)
                
                results[ticker] = {
                    "ticker": ticker,
                    "market": market,
                    "currency": market_info['currency'],
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Completed analysis for {ticker}")
                
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                results[ticker] = {
                    "ticker": ticker,
                    "error": f"Error analyzing {ticker}: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def compare_stocks(self, tickers: List[str]) -> str:
        """
        Compare multiple stocks side-by-side
        
        Args:
            tickers: List of ticker symbols (minimum 2)
            
        Returns:
            Comparative analysis
        """
        if len(tickers) < 2:
            return "Please provide at least 2 tickers to compare"
        
        logger.info(f"Comparing {len(tickers)} stocks: {', '.join(tickers)}")
        
        # Detect markets for all tickers
        markets = [self.market_detector.detect_market(t) for t in tickers]
        
        # Build comparison query
        query = AgentPrompts.get_comparison_query(tickers, markets)
        
        # Analyze with market context
        return self.analyze(query, include_market_context=True)
    
    def get_signal(self, ticker: str) -> Dict[str, str]:
        """
        Get quick buy/sell/hold signal for a ticker
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary with signal, strength, and reason
        """
        logger.info(f"Getting signal for {ticker}")
        
        market_info = self.market_detector.get_market_info(ticker)
        currency = market_info['currency']
        
        query = AgentPrompts.get_signals_query(ticker, currency)
        analysis = self.analyze(query, include_market_context=True)
        
        # Parse signal from analysis (simple extraction)
        signal = "HOLD"  # Default
        if "BUY" in analysis.upper() and "SELL" not in analysis.upper():
            signal = "BUY"
        elif "SELL" in analysis.upper():
            signal = "SELL"
        
        return {
            "ticker": ticker,
            "signal": signal,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_with_context(
        self,
        ticker: str,
        additional_context: str
    ) -> str:
        """
        Analyze a ticker with additional custom context
        
        Args:
            ticker: Ticker symbol
            additional_context: Additional context or constraints
            
        Returns:
            Analysis response
        """
        query = f"""Analyze {ticker} considering the following context:

{additional_context}

Provide technical analysis with specific entry/exit levels and risk management."""
        
        return self.analyze(query, include_market_context=True)
