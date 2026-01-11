# tools/market_data_tool.py
"""
Market data fetching tool
"""
from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel
import yfinance as yf
import logging

from .schemas import TickerInput

logger = logging.getLogger(__name__)


class GetMarketDataTool(BaseTool):
    """
    Tool to fetch current market data for stocks
    
    This tool retrieves real-time market data including:
    - Current price, open, high, low
    - Trading volume
    - Price change and percentage change
    
    Usage:
        tool = GetMarketDataTool()
        result = tool._run(ticker="AAPL", period="6mo")
    """
    
    name = "get_market_data"
    description = "Fetch current market data including price, volume, and basic stats for a stock ticker"
    args_schema: Type[BaseModel] = TickerInput
    
    def _run(self, ticker: str, period: str = "6mo") -> str:
        """
        Fetch and return market data
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for historical data
            
        Returns:
            Formatted string with market data
        """
        try:
            logger.info(f"Fetching market data for {ticker}")
            
            df = yf.download(ticker, period=period, progress=False)
            
            if df.empty:
                logger.warning(f"No data found for {ticker}")
                return f"No data found for {ticker}"
            
            latest = df.iloc[-1]
            previous = df.iloc[-2]
            
            # Calculate change
            price_change = latest['Close'] - previous['Close']
            price_change_pct = (price_change / previous['Close']) * 100
            
            result = f"""Market Data for {ticker}:
            Current Price: ${latest['Close']:.2f}
            Open: ${latest['Open']:.2f}
            High: ${latest['High']:.2f}
            Low: ${latest['Low']:.2f}
            Volume: {latest['Volume']:,.0f}
            Previous Close: ${previous['Close']:.2f}
            Change: ${price_change:.2f} ({price_change_pct:+.2f}%)"""
            
            logger.info(f"Successfully fetched data for {ticker}")
            return result
            
        except Exception as e:
            error_msg = f"Error fetching data for {ticker}: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, ticker: str, period: str = "6mo") -> str:
        """
        Async version of _run
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for historical data
            
        Returns:
            Formatted string with market data
        """
        return self._run(ticker, period)
