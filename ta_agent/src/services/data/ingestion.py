# fetch_data.py
import pandas as pd
import yfinance as yf
from datetime import datetime
import ssl
import certifi

from ...core.logging import logger
from ...core.exceptions import DataFetchError


def fetch_ohlcv(ticker: str, period: str = '5y', interval: str = '1d') -> pd.DataFrame:
    """
    Fetch OHLCV data from yfinance and return a cleaned DataFrame.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'TSLA')
        period: Time period ('1mo', '3mo', '6mo', '1y', '2y', '5y')
        interval: Data interval ('1d', '1h', '30m', etc.)
    
    Returns:
        pd.DataFrame: OHLCV data with columns [open, high, low, close, volume]
    
    Raises:
        DataFetchError: If data fetch fails
    """
    try:
        logger.info(f"Fetching data for {ticker} - Period: {period}, Interval: {interval}")
        
        # Try with SSL verification first
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        
    except Exception as e:
        logger.warning(f"SSL error for {ticker}, retrying without verification: {str(e)}")
        
        # If SSL error, try without verification
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Create a session that doesn't verify SSL
        session = requests.Session()
        session.verify = False
        
        # Suppress only the InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            # Download with custom session
            df = yf.download(ticker, period=period, interval=interval, progress=False, session=session)
        except Exception as e2:
            logger.error(f"Failed to fetch data for {ticker}: {str(e2)}")
            raise DataFetchError(f"Failed to fetch data for {ticker}: {str(e2)}")
    
    if df.empty:
        logger.error(f"No data returned for {ticker}")
        raise DataFetchError(f'No data available for {ticker}')
    
    df = df.dropna()
    df.index = pd.to_datetime(df.index)
    
    # Handle MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Normalize column names to lowercase
    df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
    
    logger.info(f"Successfully fetched {len(df)} rows for {ticker}")
    return df


def fetch_multiple_tickers(tickers: list, period: str = '1y', interval: str = '1d') -> dict:
    """
    Fetch data for multiple tickers.
    
    Args:
        tickers: List of stock symbols
        period: Time period
        interval: Data interval
    
    Returns:
        dict: {ticker: DataFrame}
    """
    results = {}
    
    for ticker in tickers:
        try:
            results[ticker] = fetch_ohlcv(ticker, period, interval)
        except DataFetchError as e:
            logger.error(f"Failed to fetch {ticker}: {str(e)}")
            results[ticker] = None
    
    return results


if __name__ == '__main__':
    # Test
    try:
        df = fetch_ohlcv('AAPL', period='1mo')
        # print(df.tail())
    except DataFetchError as e:
        print(f"Error: {e}")
