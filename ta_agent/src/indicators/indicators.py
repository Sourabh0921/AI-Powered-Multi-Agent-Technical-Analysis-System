# indicators.py
import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators for a DataFrame.
    This is a convenience function that applies all indicators at once.
    """
    df = df.copy()
    
    # Handle both lowercase and capitalized column names
    close_col = 'Close' if 'Close' in df.columns else 'close'
    high_col = 'High' if 'High' in df.columns else 'high'
    low_col = 'Low' if 'Low' in df.columns else 'low'
    volume_col = 'Volume' if 'Volume' in df.columns else 'volume'
    
    # RSI
    df['rsi'] = rsi(df[close_col])
    
    # MACD
    macd_line, signal_line, hist = macd(df[close_col])
    df['macd'] = macd_line
    df['macd_signal'] = signal_line
    df['macd_hist'] = hist
    df['vwap'] = vwap(df, high_col, low_col, close_col, volume_col)

    # Moving Averages
    df['sma_20'] = sma(df[close_col], 20)
    df['sma_50'] = sma(df[close_col], 50)
    df['sma_200'] = sma(df[close_col], 200)
    df['ema_12'] = ema(df[close_col], 12)
    df['ema_26'] = ema(df[close_col], 26)
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = bollinger_bands(df[close_col])
    df['bb_upper'] = bb_upper
    df['bb_middle'] = bb_middle
    df['bb_lower'] = bb_lower
    
    return df

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()

def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()

# def rsi(series: pd.Series, window: int = 14) -> pd.Series:
#     delta = series.diff()
#     up = delta.clip(lower=0)
#     down = -1 * delta.clip(upper=0)
#     ma_up = up.rolling(window).mean()
#     ma_down = down.rolling(window).mean()
#     rs = ma_up / ma_down
#     return 100 - (100 / (1 + rs))
def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def vwap(df: pd.DataFrame, high_col='High', low_col='Low', close_col='Close', volume_col='Volume'):
    tp = (df[high_col] + df[low_col] + df[close_col]) / 3
    vwap = (tp * df[volume_col]).cumsum() / df[volume_col].cumsum()
    return vwap


def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2):
    middle = series.rolling(window).mean()
    std = series.rolling(window).std(ddof=0)
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def detect_patterns(df: pd.DataFrame):
    """Detect common technical patterns"""
    patterns = []
    
    # Double Top/Bottom detection
    highs = df['high'].rolling(window=5, center=True).max()
    lows = df['low'].rolling(window=5, center=True).min()
    
    # Head and Shoulders detection (simplified)
    for i in range(20, len(df) - 20):
        window = df.iloc[i-20:i+20]
        if len(window) < 40:
            continue
            
        # Check for three peaks (head and shoulders)
        peaks = []
        for j in range(5, len(window) - 5):
            if window['high'].iloc[j] > window['high'].iloc[j-5:j].max() and \
               window['high'].iloc[j] > window['high'].iloc[j+1:j+6].max():
                peaks.append((window.index[j], window['high'].iloc[j]))
        
        if len(peaks) == 3:
            # Check if middle peak is highest (head)
            if peaks[1][1] > peaks[0][1] and peaks[1][1] > peaks[2][1]:
                patterns.append({
                    'type': 'Head and Shoulders',
                    'date': peaks[1][0].strftime('%Y-%m-%d'),
                    'signal': 'bearish',
                    'description': 'Bearish reversal pattern detected'
                })
    
    # Support and Resistance levels
    recent_high = df['high'].tail(50).max()
    recent_low = df['low'].tail(50).min()
    
    if df['close'].iloc[-1] >= recent_high * 0.98:
        patterns.append({
            'type': 'Near Resistance',
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'level': float(recent_high),
            'signal': 'caution',
            'description': f'Price near resistance level at ${recent_high:.2f}'
        })
    
    if df['close'].iloc[-1] <= recent_low * 1.02:
        patterns.append({
            'type': 'Near Support',
            'date': df.index[-1].strftime('%Y-%m-%d'),
            'level': float(recent_low),
            'signal': 'bullish',
            'description': f'Price near support level at ${recent_low:.2f}'
        })
    
    # Golden Cross / Death Cross
    if 'sma_50' in df.columns and 'sma_200' in df.columns:
        sma_50_prev = df['sma_50'].iloc[-2]
        sma_200_prev = df['sma_200'].iloc[-2]
        sma_50_curr = df['sma_50'].iloc[-1]
        sma_200_curr = df['sma_200'].iloc[-1]
        
        if sma_50_prev < sma_200_prev and sma_50_curr > sma_200_curr:
            patterns.append({
                'type': 'Golden Cross',
                'date': df.index[-1].strftime('%Y-%m-%d'),
                'signal': 'bullish',
                'description': '50-day SMA crossed above 200-day SMA (bullish signal)'
            })
        elif sma_50_prev > sma_200_prev and sma_50_curr < sma_200_curr:
            patterns.append({
                'type': 'Death Cross',
                'date': df.index[-1].strftime('%Y-%m-%d'),
                'signal': 'bearish',
                'description': '50-day SMA crossed below 200-day SMA (bearish signal)'
            })
    
    return patterns
