"""
Query Processing Module
Handles query classification and technical data fetching
"""
from typing import Dict, Any, Optional, List
import pandas as pd

from ..rag.rag_engine import RAGEngine
from ...ingestion.fetch_data import fetch_ohlcv
from ...signals.signals import generate_signals
from ...core.logging import logger


class QueryProcessor:
    """
    Processes queries and fetches relevant data
    
    Responsibilities:
    - Query classification
    - Ticker extraction
    - Market data fetching
    - Technical indicator calculation
    """
    
    def __init__(self, rag_engine: RAGEngine):
        """
        Initialize query processor
        
        Args:
            rag_engine: RAG engine instance for document queries
        """
        self.rag_engine = rag_engine
    
    def classify_query(self, question: str) -> Dict[str, Any]:
        """
        Classify query and extract relevant information
        
        Args:
            question: User question
            
        Returns:
            Query classification info with tickers
        """
        return self.rag_engine.query_processor.classify_query(question)
    
    def extract_tickers(
        self,
        question: str,
        provided_ticker: Optional[str] = None
    ) -> List[str]:
        """
        Extract tickers from query or use provided ticker
        
        Args:
            question: User question
            provided_ticker: Explicitly provided ticker
            
        Returns:
            List of unique ticker symbols
        """
        query_info = self.classify_query(question)
        tickers = query_info.get("tickers", [])
        
        if provided_ticker:
            tickers.append(provided_ticker)
        
        # Return unique tickers
        return list(set(tickers)) if tickers else []
    
    def fetch_technical_data(
        self,
        ticker: str,
        period: str = "3mo"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch and prepare technical data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            period: Data period
            
        Returns:
            DataFrame with OHLCV data and indicators, or None if failed
        """
        try:
            logger.info(f"📊 Fetching technical data for {ticker}")
            
            # Fetch market data
            df = fetch_ohlcv(ticker, period=period)
            
            if df is None or df.empty:
                logger.warning(f"No data available for {ticker}")
                return None
            
            # Calculate indicators and signals
            df = generate_signals(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    def get_document_insights(self, question: str) -> Dict[str, Any]:
        """
        Get insights from documents using RAG
        
        Args:
            question: User question
            
        Returns:
            RAG query result with answer and sources
        """
        logger.info("📄 Querying document knowledge base...")
        return self.rag_engine.query(question)
    
    def analyze_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract and analyze technical indicators from DataFrame
        
        Args:
            df: DataFrame with calculated indicators
            
        Returns:
            Dictionary of technical metrics
        """
        latest = df.iloc[-1]
        
        # Determine signal
        signal_value = latest.get('signal', 0)
        if signal_value == 1:
            signal = "BUY"
        elif signal_value == -1:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return {
            "current_price": float(latest['close']),
            "rsi": float(latest.get('rsi', 0)),
            "macd": float(latest.get('macd', 0)),
            "macd_signal": float(latest.get('macd_signal', 0)),
            "sma_20": float(latest.get('sma_20', 0)),
            "sma_50": float(latest.get('sma_50', 0)),
            "sma_200": float(latest.get('sma_200', 0)),
            "volume": float(latest.get('volume', 0)),
            "signal": signal
        }
