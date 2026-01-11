# fetch_data.py
import pandas as pd
import yfinance as yf
from datetime import datetime
import ssl
import certifi

def fetch_ohlcv(ticker: str, period: str = '5y', interval: str = '1d') -> pd.DataFrame:
    """Fetch OHLCV from yfinance and return a cleaned DataFrame."""
    try:
        # Try with SSL verification first
        df = yf.download(ticker, period=period, interval=interval, progress=False)
    except Exception as e:
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
        
        # Download with custom session
        df = yf.download(ticker, period=period, interval=interval, progress=False, session=session)
    
    if df.empty:
        raise ValueError(f'No data for {ticker}')
    df = df.dropna()
    df.index = pd.to_datetime(df.index)
    
    # Handle MultiIndex columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Normalize column names
    df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
    return df

if __name__ == '__main__':
    print(fetch_ohlcv('RELIANCE.NS', period='2y').tail())
