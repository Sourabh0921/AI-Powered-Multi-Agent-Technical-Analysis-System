# workflow/data_fetcher.py
"""
Data fetching and preparation for workflow
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """Fetch and prepare market data for analysis"""
    
    def __init__(self, period: str = '6mo'):
        """
        Initialize data fetcher
        
        Args:
            period: Data period (e.g., '6mo', '1y', '2y')
        """
        self.period = period
    
    def fetch_price_data(self, ticker: str) -> pd.DataFrame:
        """
        Fetch historical price data with signals
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            DataFrame with OHLCV data and optional signals
            
        Raises:
            ValueError: If no data returned
        """
        try:
            # Download data
            df = yf.download(
                ticker,
                period=self.period,
                progress=False,
                auto_adjust=False
            )
            
            # Add signals if available
            try:
                from ...signals.signals import generate_signals
                df = generate_signals(df)
                logger.info(f"Signals generated for {ticker}")
            except Exception as e:
                logger.warning(f"Signal generation skipped: {e}")
            
            # Clean data
            df = df.ffill().dropna()
            
            if df.empty:
                raise ValueError(f"No data returned for {ticker}")
            
            logger.info(f"Fetched {len(df)} rows of data for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"Data fetch failed for {ticker}: {e}")
            raise
    
    def fetch_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch fundamental data for ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with fundamental metrics
        """
        fundamentals: Dict[str, Any] = {}
        
        try:
            t = yf.Ticker(ticker)
            
            # Fast info (quick and reliable)
            fast = getattr(t, 'fast_info', {}) or {}
            fundamentals.update({
                "currency": fast.get('currency'),
                "market_cap": fast.get('market_cap'),
                "pe": fast.get('trailing_pe'),
                "shares": fast.get('shares'),
                "yield": fast.get('dividend_yield')
            })
            
            # Additional info (slower, optional)
            try:
                info = t.get_info() if hasattr(t, 'get_info') else getattr(t, 'info', {})
                for key in ["sector", "industry", "longName", "country"]:
                    if key in info:
                        fundamentals[key] = info[key]
            except Exception as e:
                logger.warning(f"Extended info fetch failed: {e}")
            
            logger.info(f"Fetched fundamentals for {ticker}")
            
        except Exception as e:
            logger.error(f"Fundamentals fetch failed for {ticker}: {e}")
        
        return fundamentals
    
    def format_fundamentals(self, fundamentals: Dict[str, Any]) -> str:
        """
        Format fundamentals as human-readable string
        
        Args:
            fundamentals: Dictionary of fundamental metrics
            
        Returns:
            Formatted string
        """
        parts = []
        
        if fundamentals.get("longName"):
            parts.append(str(fundamentals["longName"]))
        
        if fundamentals.get("sector"):
            parts.append(f"Sector: {fundamentals['sector']}")
        
        if fundamentals.get("industry"):
            parts.append(f"Industry: {fundamentals['industry']}")
        
        if fundamentals.get("market_cap"):
            parts.append(f"MktCap: {fundamentals['market_cap']}")
        
        if fundamentals.get("pe"):
            parts.append(f"PE: {fundamentals['pe']}")
        
        if fundamentals.get("yield"):
            parts.append(f"Yield: {fundamentals['yield']}")
        
        return ", ".join(parts) if parts else "N/A"
