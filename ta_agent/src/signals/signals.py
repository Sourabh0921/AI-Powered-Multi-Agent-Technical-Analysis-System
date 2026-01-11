# signals.py
import pandas as pd
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.indicators.indicators import rsi, macd, sma, ema, bollinger_bands, detect_patterns

# def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
#     df = df.copy()
    
#     # Handle both lowercase and capitalized column names
#     close_col = 'Close' if 'Close' in df.columns else 'close'
    
#     # Technical indicators
#     df['rsi'] = rsi(df[close_col])
#     macd_line, signal_line, hist = macd(df[close_col])
#     df['macd'] = macd_line
#     df['macd_signal'] = signal_line
#     df['macd_hist'] = hist
    
#     # Moving Averages
#     df['sma_20'] = sma(df[close_col], 20)
#     df['sma_50'] = sma(df[close_col], 50)
#     df['sma_200'] = sma(df[close_col], 200)
#     df['ema_12'] = ema(df[close_col], 12)
#     df['ema_26'] = ema(df[close_col], 26)
    
#     # Bollinger Bands
#     bb_upper, bb_middle, bb_lower = bollinger_bands(df[close_col])
#     df['bb_upper'] = bb_upper
#     df['bb_middle'] = bb_middle
#     df['bb_lower'] = bb_lower

#     # simple rule-based signals
#     df['signal'] = 0
#     df.loc[(df['rsi'] < 30) & (df['macd_hist'] > 0), 'signal'] = 1  # buy
#     df.loc[(df['rsi'] > 70) & (df['macd_hist'] < 0), 'signal'] = -1 # sell
#     return df

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    close_col = 'Close' if 'Close' in df.columns else 'close'

    # Indicators
    df['rsi'] = rsi(df[close_col])
    macd_line, signal_line, hist = macd(df[close_col])
    df['macd'] = macd_line
    df['macd_signal'] = signal_line
    df['macd_hist'] = hist

    df['ema_20'] = ema(df[close_col], 20)

    bb_upper, bb_middle, bb_lower = bollinger_bands(df[close_col])
    df['bb_upper'] = bb_upper
    df['bb_middle'] = bb_middle
    df['bb_lower'] = bb_lower

    # Initialize signal column
    df['signal'] = 0

    # RSI cross conditions
    rsi_cross_up = (df['rsi'].shift(1) < 30) & (df['rsi'] >= 30)
    rsi_cross_down = (df['rsi'].shift(1) > 70) & (df['rsi'] <= 70)

    # MACD histogram cross
    macd_bullish = (df['macd_hist'].shift(1) < 0) & (df['macd_hist'] > 0)
    macd_bearish = (df['macd_hist'].shift(1) > 0) & (df['macd_hist'] < 0)

    # Trend filter
    trend_up = df[close_col] > df['ema_20']
    trend_down = df[close_col] < df['ema_20']

    # Optional volatility filter
    near_lower_bb = df[close_col] <= df['bb_lower'] * 1.01
    near_upper_bb = df[close_col] >= df['bb_upper'] * 0.99

    # Buy / Sell signals
    df.loc[rsi_cross_up & macd_bullish & trend_up & near_lower_bb, 'signal'] = 1
    df.loc[rsi_cross_down & macd_bearish & trend_down & near_upper_bb, 'signal'] = -1

    return df

