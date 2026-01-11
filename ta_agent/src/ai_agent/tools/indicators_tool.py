# tools/indicators_tool.py
"""
Technical indicators calculation tool
"""
from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel
import yfinance as yf
import logging

from .schemas import TickerInput
from ...signals.signals import generate_signals

logger = logging.getLogger(__name__)


class GetTechnicalIndicatorsTool(BaseTool):
    """
    Tool to calculate technical indicators for stocks
    
    This tool calculates and returns:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - MACD Signal and Histogram
    - Buy/Sell/Hold signals
    
    Usage:
        tool = GetTechnicalIndicatorsTool()
        result = tool._run(ticker="AAPL", period="6mo")
    """
    
    name = "get_technical_indicators"
    description = "Calculate technical indicators (RSI, MACD) for a stock"
    args_schema: Type[BaseModel] = TickerInput
    
    # def _run(self, ticker: str, period: str = "6mo") -> str:
    #     """
    #     Calculate and return technical indicators
        
    #     Args:
    #         ticker: Stock ticker symbol
    #         period: Time period for calculation
            
    #     Returns:
    #         Formatted string with technical indicators
    #     """
    #     try:
    #         logger.info(f"Calculating technical indicators for {ticker}")
            
    #         df = yf.download(ticker, period=period, progress=False)
            
    #         if df.empty:
    #             logger.warning(f"No data found for {ticker}")
    #             return f"No data found for {ticker}"
            
    #         # Generate signals and indicators
    #         df = generate_signals(df)
    #         latest = df.iloc[-1]
            
    #         # Extract indicator values
    #         rsi_value = latest.get('rsi', 0)
    #         macd_value = latest.get('macd', 0)
    #         macd_signal = latest.get('macd_signal', 0)
    #         macd_hist = latest.get('macd_hist', 0)
    #         signal = latest.get('signal', 0)
            
    #         # Determine RSI interpretation
    #         if rsi_value > 70:
    #             rsi_status = "Overbought"
    #         elif rsi_value < 30:
    #             rsi_status = "Oversold"
    #         else:
    #             rsi_status = "Neutral"
            
    #         # Determine signal interpretation
    #         if signal == 1:
    #             signal_status = "BUY"
    #         elif signal == -1:
    #             signal_status = "SELL"
    #         else:
    #             signal_status = "HOLD"
            
    #         result = f"""Technical Indicators for {ticker}:
    #         RSI (14): {rsi_value:.2f} - {rsi_status}
    #         MACD: {macd_value:.4f}
    #         MACD Signal: {macd_signal:.4f}
    #         MACD Histogram: {macd_hist:.4f}
    #         Signal: {signal_status}"""
            
    #         logger.info(f"Successfully calculated indicators for {ticker}")
    #         return result
            
    #     except Exception as e:
    #         error_msg = f"Error calculating indicators for {ticker}: {str(e)}"
    #         logger.error(error_msg)
    #         return error_msg
    def _run(self, ticker: str, period: str = "6mo") -> str:
        try:
            logger.info(f"Calculating technical indicators for {ticker}")

            # NSE/BSE support
            if ticker.isupper() and not ticker.endswith((".NS", ".BO")):
                logger.info("Assuming NSE ticker format")
            
            df = yf.download(ticker, period=period, progress=False)

            if df.empty:
                return f"No data found for {ticker}"

            df = df.dropna()

            # Generate indicators & signals
            df = generate_signals(df)

            latest = df.dropna().iloc[-1]

            rsi_value = float(latest['rsi'])
            macd_hist = float(latest['macd_hist'])
            signal = int(latest['signal'])

            # Interpret RSI
            if rsi_value > 70:
                rsi_status = "Overbought"
            elif rsi_value < 30:
                rsi_status = "Oversold"
            else:
                rsi_status = "Neutral"

            # Signal explanation
            if signal == 1:
                signal_status = "BUY"
                reasoning = "RSI rebounded from oversold and MACD momentum turned positive"
            elif signal == -1:
                signal_status = "SELL"
                reasoning = "RSI fell from overbought and MACD momentum turned negative"
            else:
                signal_status = "HOLD"
                reasoning = "No strong momentum or trend confirmation"

            return f"""
            Technical Indicators for {ticker}

            RSI (14): {rsi_value:.2f} ({rsi_status})
            MACD Histogram: {macd_hist:.4f}

            Final Signal: {signal_status}
            Reason: {reasoning}
            """.strip()

        except Exception as e:
            logger.exception("Indicator tool failed")
            return f"Error calculating indicators for {ticker}: {str(e)}"

    async def _arun(self, ticker: str, period: str = "6mo") -> str:
        """
        Async version of _run
        
        Args:
            ticker: Stock ticker symbol
            period: Time period for calculation
            
        Returns:
            Formatted string with technical indicators
        """
        return self._run(ticker, period)
