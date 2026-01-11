# agents/utils.py
"""
Utility functions for agent operations
Helper functions for ticker extraction, validation, and formatting
"""
import re
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


class TickerExtractor:
    """
    Utility for extracting and validating ticker symbols from text
    """
    
    # Common words that might match ticker pattern but aren't tickers
    EXCLUDE_WORDS = {
        'THE', 'AND', 'FOR', 'WITH', 'WHAT', 'BUY', 'SELL', 'HOLD',
        'RSI', 'MACD', 'SMA', 'EMA', 'ATR', 'ADX', 'VWAP', 'OBV',
        'MA', 'BB', 'KST', 'ROC', 'MFI', 'CCI', 'STOCH',
        'USD', 'INR', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD',
        'NYSE', 'NSE', 'BSE', 'NASDAQ', 'LSE', 'TSE', 'TSX',
        'API', 'ETF', 'IPO', 'CEO', 'CFO', 'AI', 'ML', 'IT',
        'USA', 'UK', 'EU', 'FII', 'DII', 'GDP', 'CPI', 'PPI'
    }
    
    @staticmethod
    def extract_tickers(text: str) -> List[str]:
        """
        Extract ticker symbols from text
        
        Recognizes patterns like:
        - AAPL
        - RELIANCE.NS
        - HSBC.L
        - SONY.T
        
        Args:
            text: Text to extract tickers from
            
        Returns:
            List of unique ticker symbols found
            
        Examples:
            >>> TickerExtractor.extract_tickers("Analyze AAPL and MSFT")
            ['AAPL', 'MSFT']
            >>> TickerExtractor.extract_tickers("Compare RELIANCE.NS with TCS.NS")
            ['RELIANCE.NS', 'TCS.NS']
        """
        # Pattern for tickers: uppercase letters optionally followed by .XX suffix
        pattern = r'\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b'
        tickers = re.findall(pattern, text.upper())
        
        # Filter out common words
        tickers = [t for t in tickers if t not in TickerExtractor.EXCLUDE_WORDS]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tickers = []
        for ticker in tickers:
            if ticker not in seen:
                seen.add(ticker)
                unique_tickers.append(ticker)
        
        logger.debug(f"Extracted {len(unique_tickers)} tickers from text")
        return unique_tickers
    
    @staticmethod
    def validate_ticker_format(ticker: str) -> bool:
        """
        Validate if a string matches ticker format
        
        Args:
            ticker: Ticker string to validate
            
        Returns:
            True if valid ticker format
        """
        pattern = r'^[A-Z]{1,5}(?:\.[A-Z]{1,3})?$'
        return bool(re.match(pattern, ticker.upper()))
    
    @staticmethod
    def normalize_ticker(ticker: str) -> str:
        """
        Normalize ticker to standard format (uppercase)
        
        Args:
            ticker: Ticker to normalize
            
        Returns:
            Normalized ticker
        """
        return ticker.upper().strip()
    
    @staticmethod
    def split_ticker_and_suffix(ticker: str) -> tuple:
        """
        Split ticker into base symbol and market suffix
        
        Args:
            ticker: Full ticker (e.g., "RELIANCE.NS")
            
        Returns:
            Tuple of (base_symbol, suffix)
            
        Examples:
            >>> TickerExtractor.split_ticker_and_suffix("RELIANCE.NS")
            ('RELIANCE', '.NS')
            >>> TickerExtractor.split_ticker_and_suffix("AAPL")
            ('AAPL', '')
        """
        parts = ticker.split('.')
        if len(parts) == 2:
            return (parts[0], f'.{parts[1]}')
        return (ticker, '')


class TextFormatter:
    """
    Utility for formatting analysis text output
    """
    
    @staticmethod
    def format_price(price: float, currency: str = "USD") -> str:
        """
        Format price with currency symbol
        
        Args:
            price: Price value
            currency: Currency code
            
        Returns:
            Formatted price string
        """
        currency_symbols = {
            "USD": "$",
            "INR": "₹",
            "EUR": "€",
            "GBP": "£",
            "JPY": "¥",
            "CAD": "C$",
            "AUD": "A$"
        }
        
        symbol = currency_symbols.get(currency, currency)
        
        if currency == "INR":
            # Indian numbering system
            return f"{symbol}{price:,.2f}"
        else:
            return f"{symbol}{price:,.2f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """
        Format percentage value
        
        Args:
            value: Percentage value
            decimals: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.{decimals}f}%"
    
    @staticmethod
    def create_section_header(title: str, level: int = 2) -> str:
        """
        Create a markdown section header
        
        Args:
            title: Section title
            level: Header level (1-6)
            
        Returns:
            Formatted header string
        """
        return f"{'#' * level} {title}\n"
    
    @staticmethod
    def create_divider(length: int = 80, char: str = "-") -> str:
        """Create a text divider line"""
        return char * length


class WeightValidator:
    """
    Utility for validating and normalizing portfolio weights
    """
    
    @staticmethod
    def validate_weights(weights: dict, tolerance: float = 0.01) -> bool:
        """
        Validate that weights sum to 1.0
        
        Args:
            weights: Dictionary of ticker to weight
            tolerance: Acceptable deviation from 1.0
            
        Returns:
            True if weights are valid
        """
        total = sum(weights.values())
        return abs(total - 1.0) <= tolerance
    
    @staticmethod
    def normalize_weights(weights: dict) -> dict:
        """
        Normalize weights to sum to 1.0
        
        Args:
            weights: Dictionary of ticker to weight
            
        Returns:
            Normalized weights dictionary
        """
        total = sum(weights.values())
        if total == 0:
            # Equal weights if all zero
            n = len(weights)
            return {ticker: 1.0/n for ticker in weights.keys()}
        
        return {ticker: weight/total for ticker, weight in weights.items()}
    
    @staticmethod
    def create_equal_weights(tickers: list) -> dict:
        """
        Create equal weights for a list of tickers
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary with equal weights
        """
        weight = 1.0 / len(tickers) if tickers else 0
        return {ticker: weight for ticker in tickers}
