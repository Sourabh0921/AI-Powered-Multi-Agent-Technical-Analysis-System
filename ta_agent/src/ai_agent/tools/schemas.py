# tools/schemas.py
"""
Input schemas for LangChain tools
"""
from pydantic import BaseModel, Field


class TickerInput(BaseModel):
    """
    Input schema for ticker-based tools
    
    Attributes:
        ticker: Stock ticker symbol (e.g., AAPL, RELIANCE.NS, TCS.NS)
        period: Time period for data (e.g., 1mo, 3mo, 6mo, 1y)
    """
    ticker: str = Field(
        description="Stock ticker symbol (e.g., RELIANCE.NS, TCS.NS, WIPRO.NS, JIOFIN.NS)"
    )
    period: str = Field(
        default="6mo",
        description="Time period (e.g., 1mo, 3mo, 6mo, 1y)"
    )


class BacktestInput(BaseModel):
    """
    Input schema for backtesting tools
    
    Attributes:
        ticker: Stock ticker symbol
        period: Time period for backtest
        initial_capital: Starting capital for backtest
    """
    ticker: str = Field(
        description="Stock ticker symbol"
    )
    period: str = Field(
        default="1y",
        description="Time period for backtest (e.g., 6mo, 1y, 2y)"
    )
    initial_capital: float = Field(
        default=100000.0,
        description="Starting capital for backtest"
    )
