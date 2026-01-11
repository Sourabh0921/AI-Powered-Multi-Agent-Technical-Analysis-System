# agents/market_info.py
"""
Market information and detection utilities
Handles market-specific data for different exchanges worldwide
"""
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class MarketInfo:
    """
    Market information database
    Contains details about different exchanges worldwide
    """
    
    # Market information database
    MARKETS = {
        "NSE": {
            "name": "National Stock Exchange of India",
            "suffix": ".NS",
            "currency": "INR",
            "timezone": "Asia/Kolkata",
            "trading_hours": "9:15 AM - 3:30 PM IST",
            "characteristics": "High retail participation, influenced by FII/DII flows, regulatory focus on corporate governance"
        },
        "BSE": {
            "name": "Bombay Stock Exchange",
            "suffix": ".BO",
            "currency": "INR",
            "timezone": "Asia/Kolkata",
            "trading_hours": "9:15 AM - 3:30 PM IST",
            "characteristics": "One of Asia's oldest exchanges, large mid-cap and small-cap universe"
        },
        "US": {
            "name": "US Markets (NYSE/NASDAQ)",
            "suffix": "",
            "currency": "USD",
            "timezone": "America/New_York",
            "trading_hours": "9:30 AM - 4:00 PM ET",
            "characteristics": "World's largest market, high liquidity, influenced by Fed policy and macroeconomic data"
        },
        "LSE": {
            "name": "London Stock Exchange",
            "suffix": ".L",
            "currency": "GBP",
            "timezone": "Europe/London",
            "trading_hours": "8:00 AM - 4:30 PM GMT",
            "characteristics": "Major European exchange, influenced by Brexit and European economic policy"
        },
        "TSE": {
            "name": "Tokyo Stock Exchange",
            "suffix": ".T",
            "currency": "JPY",
            "timezone": "Asia/Tokyo",
            "trading_hours": "9:00 AM - 3:00 PM JST",
            "characteristics": "Asia's largest exchange, influenced by BoJ policy and export dynamics"
        },
        "TSX": {
            "name": "Toronto Stock Exchange",
            "suffix": ".TO",
            "currency": "CAD",
            "timezone": "America/Toronto",
            "trading_hours": "9:30 AM - 4:00 PM ET",
            "characteristics": "Strong in resources and financials, influenced by commodity prices"
        }
    }
    
    @classmethod
    def get_all_markets(cls) -> Dict[str, Dict]:
        """Get all market information"""
        return cls.MARKETS
    
    @classmethod
    def get_market_info(cls, market_code: str) -> Dict:
        """
        Get information for a specific market
        
        Args:
            market_code: Market code (NSE, BSE, US, etc.)
            
        Returns:
            Market information dictionary
        """
        return cls.MARKETS.get(market_code, cls.MARKETS["US"])
    
    @classmethod
    def get_market_names(cls) -> list:
        """Get list of all supported market names"""
        return list(cls.MARKETS.keys())


class MarketDetector:
    """
    Market detection utility
    Identifies which exchange a ticker belongs to based on suffix
    """
    
    def __init__(self):
        self.markets = MarketInfo.get_all_markets()
        logger.info(f"MarketDetector initialized with {len(self.markets)} markets")
    
    def detect_market(self, ticker: str) -> str:
        """
        Detect which market a ticker belongs to based on suffix
        
        Args:
            ticker: Ticker symbol (e.g., "AAPL", "RELIANCE.NS", "HSBC.L")
            
        Returns:
            Market code (NSE, BSE, US, LSE, TSE, TSX)
            
        Examples:
            >>> detector = MarketDetector()
            >>> detector.detect_market("RELIANCE.NS")
            'NSE'
            >>> detector.detect_market("AAPL")
            'US'
            >>> detector.detect_market("HSBC.L")
            'LSE'
        """
        ticker_upper = ticker.upper()
        
        # Check for known suffixes
        if ".NS" in ticker_upper:
            return "NSE"
        elif ".BO" in ticker_upper:
            return "BSE"
        elif ".L" in ticker_upper:
            return "LSE"
        elif ".T" in ticker_upper:
            return "TSE"
        elif ".TO" in ticker_upper:
            return "TSX"
        else:
            # Default to US market for tickers without suffix
            return "US"
    
    def get_market_info(self, ticker: str) -> Dict:
        """
        Get market information for a specific ticker
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Market information dictionary
        """
        market = self.detect_market(ticker)
        return MarketInfo.get_market_info(market)
    
    def get_market_context(self, ticker: str) -> str:
        """
        Get formatted market context string for a ticker
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Formatted context string with market details
        """
        market = self.detect_market(ticker)
        info = MarketInfo.get_market_info(market)
        
        context = f"""
Market Context for {ticker}:
- Exchange: {info['name']}
- Currency: {info['currency']}
- Trading Hours: {info['trading_hours']} ({info['timezone']})
- Market Characteristics: {info['characteristics']}
"""
        return context
    
    def get_currency(self, ticker: str) -> str:
        """
        Get the currency for a ticker's market
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Currency code (USD, INR, GBP, etc.)
        """
        info = self.get_market_info(ticker)
        return info['currency']
    
    def is_indian_market(self, ticker: str) -> bool:
        """Check if ticker is from Indian market (NSE or BSE)"""
        market = self.detect_market(ticker)
        return market in ["NSE", "BSE"]
    
    def is_us_market(self, ticker: str) -> bool:
        """Check if ticker is from US market"""
        market = self.detect_market(ticker)
        return market == "US"
    
    def batch_detect_markets(self, tickers: list) -> Dict[str, str]:
        """
        Detect markets for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary mapping ticker to market code
        """
        return {ticker: self.detect_market(ticker) for ticker in tickers}
    
    def get_market_distribution(self, tickers: list, weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calculate market distribution across a list of tickers
        
        Args:
            tickers: List of ticker symbols
            weights: Optional weights for each ticker
            
        Returns:
            Dictionary mapping market to percentage allocation
        """
        if weights is None:
            weights = {ticker: 1.0 / len(tickers) for ticker in tickers}
        
        distribution = {}
        for ticker in tickers:
            market = self.detect_market(ticker)
            distribution[market] = distribution.get(market, 0) + weights.get(ticker, 0)
        
        return distribution
