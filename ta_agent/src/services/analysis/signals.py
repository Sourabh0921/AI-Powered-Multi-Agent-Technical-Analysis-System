# signals.py
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from .indicators import rsi, macd
from ...core.logging import logger
from ...core.exceptions import AnalysisError


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate buy/sell signals based on RSI and MACD indicators.
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        DataFrame with added indicators and signals
    
    Signal Logic:
        - BUY (1): RSI < 30 and MACD crosses above signal
        - SELL (-1): RSI > 70 and MACD crosses below signal
        - HOLD (0): Otherwise
    """
    try:
        logger.debug(f"Generating signals for {len(df)} data points")
        
        # Calculate indicators
        df['rsi'] = rsi(df['close'], period=14)
        macd_line, signal_line, hist = macd(df['close'])
        df['macd'] = macd_line
        df['macd_signal'] = signal_line
        df['macd_hist'] = hist
        
        # Initialize signal column
        df['signal'] = 0
        
        # Generate signals
        # BUY: RSI < 30 (oversold) and MACD crosses above signal line
        buy_condition = (df['rsi'] < 30) & (df['macd'] > df['macd_signal'])
        df.loc[buy_condition, 'signal'] = 1
        
        # SELL: RSI > 70 (overbought) and MACD crosses below signal line
        sell_condition = (df['rsi'] > 70) & (df['macd'] < df['macd_signal'])
        df.loc[sell_condition, 'signal'] = -1
        
        logger.debug(f"Generated {(df['signal'] == 1).sum()} BUY signals, "
                    f"{(df['signal'] == -1).sum()} SELL signals")
        
        return df
        
    except Exception as e:
        logger.error(f"Error generating signals: {str(e)}")
        raise AnalysisError(f"Failed to generate signals: {str(e)}")


def get_latest_signal(df: pd.DataFrame) -> dict:
    """
    Get the latest trading signal with details.
    
    Args:
        df: DataFrame with signals
    
    Returns:
        dict with signal details
    """
    try:
        latest = df.iloc[-1]
        
        signal_value = latest.get('signal', 0)
        signal_text = 'BUY' if signal_value == 1 else 'SELL' if signal_value == -1 else 'HOLD'
        
        return {
            'signal': signal_text,
            'signal_value': int(signal_value),
            'rsi': float(latest.get('rsi', 0)),
            'macd': float(latest.get('macd', 0)),
            'macd_signal': float(latest.get('macd_signal', 0)),
            'price': float(latest['close']),
            'timestamp': str(latest.name)
        }
    except Exception as e:
        logger.error(f"Error getting latest signal: {str(e)}")
        raise AnalysisError(f"Failed to get latest signal: {str(e)}")


def scan_for_signals(dfs: dict) -> list:
    """
    Scan multiple tickers for trading signals.
    
    Args:
        dfs: Dictionary of {ticker: DataFrame}
    
    Returns:
        List of tickers with actionable signals (BUY or SELL)
    """
    results = []
    
    for ticker, df in dfs.items():
        if df is not None and not df.empty:
            try:
                df_with_signals = generate_signals(df)
                signal = get_latest_signal(df_with_signals)
                
                if signal['signal'] != 'HOLD':
                    results.append({
                        'ticker': ticker,
                        **signal
                    })
            except AnalysisError as e:
                logger.warning(f"Failed to analyze {ticker}: {str(e)}")
    
    return results
