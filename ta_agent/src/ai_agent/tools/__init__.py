# tools/__init__.py
"""
Tools Package - LangChain tools for AI agent interactions
"""

from .market_data_tool import GetMarketDataTool
from .indicators_tool import GetTechnicalIndicatorsTool
from .patterns_tool import DetectPatternsTool
from .schemas import TickerInput

# Collection of all tools
ta_tools = [
    GetMarketDataTool(),
    GetTechnicalIndicatorsTool(),
    DetectPatternsTool(),
]

__all__ = [
    'GetMarketDataTool',
    'GetTechnicalIndicatorsTool',
    'DetectPatternsTool',
    'CalculateBacktestTool',
    'TickerInput',
    'ta_tools',
]
