# patterns.py
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

def detect_swing_points(close: pd.Series, order: int = 5):
    highs_idx = argrelextrema(close.values, np.greater, order=order)[0]
    lows_idx = argrelextrema(close.values, np.less, order=order)[0]
    return highs_idx, lows_idx

def detect_breakout(df: pd.DataFrame, lookback: int = 20):
    """Simple breakout: price closes above the highest high of lookback period."""
    hh = df['high'].rolling(window=lookback).max().shift(1)
    ll = df['low'].rolling(window=lookback).min().shift(1)
    breakout_up = df['close'] > hh
    breakout_down = df['close'] < ll
    return breakout_up, breakout_down
