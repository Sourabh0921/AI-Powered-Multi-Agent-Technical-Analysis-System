# tools/patterns_tool.py
"""
Chart pattern detection tool
"""
from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel
import yfinance as yf
import logging

from .schemas import TickerInput
from ...patterns.patterns import detect_breakout

logger = logging.getLogger(__name__)


class DetectPatternsTool(BaseTool):
    """
    Tool to detect technical chart patterns
    
    This tool detects:
    - Bullish breakouts (price above 20-day high)
    - Bearish breakdowns (price below 20-day low)
    - Trend analysis using moving averages
    - Support and resistance levels
    
    Usage:
        tool = DetectPatternsTool()
        result = tool._run(ticker="AAPL", period="6mo")
    """
    
    name = "detect_patterns"
    description = "Detect technical chart patterns like breakouts"
    args_schema: Type[BaseModel] = TickerInput
    
    def _run(self, ticker: str, period: str = "6mo") -> str:
        """
        Detect chart patterns
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for pattern detection
            
        Returns:
            Formatted string with pattern detection results
        """
        try:
            logger.info(f"Detecting patterns for {ticker}")
            
            df = yf.download(ticker, period=period, progress=False)
            
            if df.empty:
                logger.warning(f"No data found for {ticker}")
                return f"No data found for {ticker}"
            
            # Normalize column names to lowercase
            df.columns = [c.lower() for c in df.columns]
            
            # Detect breakout patterns
            breakout_up, breakout_down = detect_breakout(df)
            
            latest_breakout_up = breakout_up.iloc[-1] if not breakout_up.empty else False
            latest_breakout_down = breakout_down.iloc[-1] if not breakout_down.empty else False
            
            # Build result string
            result = f"Pattern Detection for {ticker}:\n\n"
            
            # Breakout detection
            if latest_breakout_up:
                result += "⚠️ BULLISH BREAKOUT detected (price above 20-day high)\n"
            elif latest_breakout_down:
                result += "⚠️ BEARISH BREAKDOWN detected (price below 20-day low)\n"
            else:
                result += "No significant breakout pattern detected\n"
            
            # Calculate moving averages
            current_price = df['close'].iloc[-1]
            sma20 = df['close'].rolling(20).mean().iloc[-1]
            sma50 = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            
            result += f"\nPrice: ${current_price:.2f}\n"
            result += f"20-day SMA: ${sma20:.2f}\n"
            
            if sma50 is not None:
                result += f"50-day SMA: ${sma50:.2f}\n"
                
                # Trend analysis
                if current_price > sma20 > sma50:
                    trend = "Bullish (Strong uptrend)"
                elif current_price < sma20 < sma50:
                    trend = "Bearish (Strong downtrend)"
                elif current_price > sma20:
                    trend = "Bullish (Moderate)"
                elif current_price < sma20:
                    trend = "Bearish (Moderate)"
                else:
                    trend = "Mixed (Sideways)"
            else:
                # Simple trend without 50-day SMA
                if current_price > sma20:
                    trend = "Bullish"
                elif current_price < sma20:
                    trend = "Bearish"
                else:
                    trend = "Neutral"
            
            result += f"Trend: {trend}"
            
            logger.info(f"Successfully detected patterns for {ticker}")
            return result
            
        except Exception as e:
            error_msg = f"Error detecting patterns for {ticker}: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, ticker: str, period: str = "6mo") -> str:
        """
        Async version of _run
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for pattern detection
            
        Returns:
            Formatted string with pattern detection results
        """
        return self._run(ticker, period)
