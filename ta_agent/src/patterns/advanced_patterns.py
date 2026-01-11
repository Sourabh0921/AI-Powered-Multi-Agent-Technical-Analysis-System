"""
Advanced Pattern Detection Module

This module implements technical chart pattern recognition using price action analysis.
Patterns are detected based on swing points, price structure, and volume confirmation.

Supported Patterns:
- Reversal: Head & Shoulders, Inverse H&S, Double Top, Double Bottom
- Continuation: Ascending Triangle, Descending Triangle, Symmetric Triangle, Flags, Wedges
- Candlestick: Doji, Hammer, Shooting Star, Engulfing patterns
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Pattern:
    """Data class for detected patterns"""
    name: str
    type: str  # 'reversal', 'continuation', 'candlestick'
    signal: str  # 'bullish', 'bearish', 'neutral'
    confidence: float  # 0-100
    description: str
    start_date: str
    end_date: str
    key_levels: Dict[str, float]  # Support, resistance, target levels
    volume_confirmed: bool


class PatternDetector:
    """Main class for detecting chart patterns"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize pattern detector with OHLCV data
        
        Args:
            df: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        """
        self.df = df.copy()
        self.patterns: List[Pattern] = []
        self._find_swing_points()
    
    def _find_swing_points(self, order: int = 5):
        """
        Find swing highs and lows using local extrema
        
        Args:
            order: How many points on each side to use for comparison
        """
        # Find swing highs (peaks)
        self.swing_highs_idx = argrelextrema(
            self.df['high'].values, 
            np.greater, 
            order=order
        )[0]
        
        # Find swing lows (troughs)
        self.swing_lows_idx = argrelextrema(
            self.df['low'].values, 
            np.less, 
            order=order
        )[0]
        
        # Store swing points with their values
        self.swing_highs = [(idx, self.df['high'].iloc[idx]) for idx in self.swing_highs_idx]
        self.swing_lows = [(idx, self.df['low'].iloc[idx]) for idx in self.swing_lows_idx]
    
    def detect_all_patterns(self) -> List[Pattern]:
        """Detect all supported patterns and return list"""
        self.patterns = []
        
        # Reversal patterns
        self.detect_head_and_shoulders()
        self.detect_inverse_head_and_shoulders()
        self.detect_double_top()
        self.detect_double_bottom()
        
        # Continuation patterns
        self.detect_ascending_triangle()
        self.detect_descending_triangle()
        self.detect_symmetric_triangle()
        self.detect_bull_flag()
        self.detect_bear_flag()
        self.detect_rising_wedge()
        self.detect_falling_wedge()
        
        # Candlestick patterns
        self.detect_doji()
        self.detect_hammer()
        self.detect_shooting_star()
        self.detect_engulfing()
        
        return self.patterns
    
    def _check_volume_confirmation(self, start_idx: int, end_idx: int) -> bool:
        """
        Check if pattern has volume confirmation
        Volume should increase during pattern formation
        """
        if end_idx >= len(self.df):
            return False
            
        pattern_volume = self.df['volume'].iloc[start_idx:end_idx].mean()
        previous_volume = self.df['volume'].iloc[max(0, start_idx-20):start_idx].mean()
        
        return pattern_volume > previous_volume * 1.1  # 10% volume increase
    
    # ==================== REVERSAL PATTERNS ====================
    
    def detect_head_and_shoulders(self):
        """
        Head and Shoulders Pattern Detection
        
        Structure: Left Shoulder - Head - Right Shoulder with neckline
        Signal: Bearish reversal
        
        Criteria:
        1. Three consecutive peaks
        2. Middle peak (head) is highest
        3. Left and right shoulders at similar heights
        4. Neckline connects two troughs
        5. Volume decreases from left shoulder to right shoulder
        """
        if len(self.swing_highs) < 3:
            return
        
        # Check recent swing highs for H&S pattern
        for i in range(len(self.swing_highs) - 2):
            left_shoulder = self.swing_highs[i]
            head = self.swing_highs[i + 1]
            right_shoulder = self.swing_highs[i + 2]
            
            ls_idx, ls_price = left_shoulder
            h_idx, h_price = head
            rs_idx, rs_price = right_shoulder
            
            # Check if head is highest
            if h_price <= ls_price or h_price <= rs_price:
                continue
            
            # Check if shoulders are at similar heights (within 5%)
            shoulder_diff = abs(ls_price - rs_price) / ls_price
            if shoulder_diff > 0.05:
                continue
            
            # Find neckline (troughs between peaks)
            troughs_between = [
                (idx, price) for idx, price in self.swing_lows 
                if ls_idx < idx < rs_idx
            ]
            
            if len(troughs_between) < 2:
                continue
            
            # Neckline is line connecting two troughs
            neckline_left = troughs_between[0]
            neckline_right = troughs_between[-1]
            
            # Check volume confirmation
            volume_confirmed = self._check_volume_confirmation(ls_idx, rs_idx)
            
            # Calculate target (distance from head to neckline)
            neckline_avg = (neckline_left[1] + neckline_right[1]) / 2
            target = neckline_avg - (h_price - neckline_avg)
            
            pattern = Pattern(
                name="Head and Shoulders",
                type="reversal",
                signal="bearish",
                confidence=75 if volume_confirmed else 60,
                description="Bearish reversal pattern. Head is highest peak with two lower shoulders. Expect breakdown below neckline.",
                start_date=self.df.index[ls_idx].strftime('%Y-%m-%d'),
                end_date=self.df.index[rs_idx].strftime('%Y-%m-%d'),
                key_levels={
                    'left_shoulder': float(ls_price),
                    'head': float(h_price),
                    'right_shoulder': float(rs_price),
                    'neckline': float(neckline_avg),
                    'target': float(target)
                },
                volume_confirmed=volume_confirmed
            )
            
            self.patterns.append(pattern)
    
    def detect_inverse_head_and_shoulders(self):
        """
        Inverse Head and Shoulders Pattern Detection
        
        Structure: Inverted H&S - bullish reversal
        Signal: Bullish reversal
        
        Similar to H&S but inverted (troughs instead of peaks)
        """
        if len(self.swing_lows) < 3:
            return
        
        for i in range(len(self.swing_lows) - 2):
            left_shoulder = self.swing_lows[i]
            head = self.swing_lows[i + 1]
            right_shoulder = self.swing_lows[i + 2]
            
            ls_idx, ls_price = left_shoulder
            h_idx, h_price = head
            rs_idx, rs_price = right_shoulder
            
            # Check if head is lowest
            if h_price >= ls_price or h_price >= rs_price:
                continue
            
            # Check if shoulders are at similar heights (within 5%)
            shoulder_diff = abs(ls_price - rs_price) / ls_price
            if shoulder_diff > 0.05:
                continue
            
            # Find neckline (peaks between troughs)
            peaks_between = [
                (idx, price) for idx, price in self.swing_highs 
                if ls_idx < idx < rs_idx
            ]
            
            if len(peaks_between) < 2:
                continue
            
            neckline_left = peaks_between[0]
            neckline_right = peaks_between[-1]
            neckline_avg = (neckline_left[1] + neckline_right[1]) / 2
            
            volume_confirmed = self._check_volume_confirmation(ls_idx, rs_idx)
            
            # Calculate target (distance from head to neckline)
            target = neckline_avg + (neckline_avg - h_price)
            
            pattern = Pattern(
                name="Inverse Head and Shoulders",
                type="reversal",
                signal="bullish",
                confidence=75 if volume_confirmed else 60,
                description="Bullish reversal pattern. Head is lowest trough with two higher shoulders. Expect breakout above neckline.",
                start_date=self.df.index[ls_idx].strftime('%Y-%m-%d'),
                end_date=self.df.index[rs_idx].strftime('%Y-%m-%d'),
                key_levels={
                    'left_shoulder': float(ls_price),
                    'head': float(h_price),
                    'right_shoulder': float(rs_price),
                    'neckline': float(neckline_avg),
                    'target': float(target)
                },
                volume_confirmed=volume_confirmed
            )
            
            self.patterns.append(pattern)
    
    def detect_double_top(self):
        """
        Double Top Pattern Detection
        
        Structure: Two peaks at similar heights with trough between
        Signal: Bearish reversal
        
        Criteria:
        1. Two peaks at approximately same level (within 2%)
        2. Clear trough between peaks
        3. Second peak on declining volume
        """
        if len(self.swing_highs) < 2:
            return
        
        for i in range(len(self.swing_highs) - 1):
            first_top = self.swing_highs[i]
            second_top = self.swing_highs[i + 1]
            
            ft_idx, ft_price = first_top
            st_idx, st_price = second_top
            
            # Check if tops are at similar heights (within 2%)
            price_diff = abs(ft_price - st_price) / ft_price
            if price_diff > 0.02:
                continue
            
            # Find trough between tops
            troughs_between = [
                (idx, price) for idx, price in self.swing_lows 
                if ft_idx < idx < st_idx
            ]
            
            if not troughs_between:
                continue
            
            trough = min(troughs_between, key=lambda x: x[1])
            support_level = trough[1]
            
            volume_confirmed = self._check_volume_confirmation(ft_idx, st_idx)
            
            # Target is distance from top to support projected downward
            target = support_level - (ft_price - support_level)
            
            pattern = Pattern(
                name="Double Top",
                type="reversal",
                signal="bearish",
                confidence=70 if volume_confirmed else 55,
                description="Bearish reversal pattern. Two peaks at similar levels. Expect breakdown below support.",
                start_date=self.df.index[ft_idx].strftime('%Y-%m-%d'),
                end_date=self.df.index[st_idx].strftime('%Y-%m-%d'),
                key_levels={
                    'first_top': float(ft_price),
                    'second_top': float(st_price),
                    'support': float(support_level),
                    'target': float(target)
                },
                volume_confirmed=volume_confirmed
            )
            
            self.patterns.append(pattern)
    
    def detect_double_bottom(self):
        """
        Double Bottom Pattern Detection
        
        Structure: Two troughs at similar depths with peak between
        Signal: Bullish reversal
        """
        if len(self.swing_lows) < 2:
            return
        
        for i in range(len(self.swing_lows) - 1):
            first_bottom = self.swing_lows[i]
            second_bottom = self.swing_lows[i + 1]
            
            fb_idx, fb_price = first_bottom
            sb_idx, sb_price = second_bottom
            
            # Check if bottoms are at similar depths (within 2%)
            price_diff = abs(fb_price - sb_price) / fb_price
            if price_diff > 0.02:
                continue
            
            # Find peak between bottoms
            peaks_between = [
                (idx, price) for idx, price in self.swing_highs 
                if fb_idx < idx < sb_idx
            ]
            
            if not peaks_between:
                continue
            
            peak = max(peaks_between, key=lambda x: x[1])
            resistance_level = peak[1]
            
            volume_confirmed = self._check_volume_confirmation(fb_idx, sb_idx)
            
            # Target is distance from bottom to resistance projected upward
            target = resistance_level + (resistance_level - fb_price)
            
            pattern = Pattern(
                name="Double Bottom",
                type="reversal",
                signal="bullish",
                confidence=70 if volume_confirmed else 55,
                description="Bullish reversal pattern. Two troughs at similar levels. Expect breakout above resistance.",
                start_date=self.df.index[fb_idx].strftime('%Y-%m-%d'),
                end_date=self.df.index[sb_idx].strftime('%Y-%m-%d'),
                key_levels={
                    'first_bottom': float(fb_price),
                    'second_bottom': float(sb_price),
                    'resistance': float(resistance_level),
                    'target': float(target)
                },
                volume_confirmed=volume_confirmed
            )
            
            self.patterns.append(pattern)
    
    # ==================== CONTINUATION PATTERNS ====================
    
    def detect_ascending_triangle(self):
        """
        Ascending Triangle Pattern Detection
        
        Structure: Flat top (resistance) with rising lows
        Signal: Bullish continuation
        
        Criteria:
        1. Horizontal resistance line (multiple touches)
        2. Upward sloping support line
        3. Decreasing volume during consolidation
        4. Breakout above resistance with volume spike
        """
        if len(self.swing_highs) < 3 or len(self.swing_lows) < 3:
            return
        
        # Check recent 50 bars for triangle formation
        recent_data = self.df.tail(50)
        if len(recent_data) < 30:
            return
        
        # Find resistance level (multiple highs at same level)
        recent_highs = [price for idx, price in self.swing_highs if idx >= len(self.df) - 50]
        
        if len(recent_highs) < 3:
            return
        
        # Check if highs are relatively flat (within 1%)
        resistance = max(recent_highs)
        flat_highs = [h for h in recent_highs if abs(h - resistance) / resistance < 0.01]
        
        if len(flat_highs) < 2:
            return
        
        # Check if lows are rising
        recent_lows = [price for idx, price in self.swing_lows if idx >= len(self.df) - 50]
        
        if len(recent_lows) < 2:
            return
        
        # Lows should be ascending
        if recent_lows[-1] <= recent_lows[0]:
            return
        
        support = min(recent_lows)
        
        # Check if currently in consolidation
        current_price = self.df['close'].iloc[-1]
        if current_price < support or current_price > resistance * 1.02:
            return
        
        # Target after breakout = height of triangle
        height = resistance - support
        target = resistance + height
        
        pattern = Pattern(
            name="Ascending Triangle",
            type="continuation",
            signal="bullish",
            confidence=65,
            description="Bullish continuation pattern. Flat resistance with rising support. Expect upside breakout.",
            start_date=self.df.index[-50].strftime('%Y-%m-%d'),
            end_date=self.df.index[-1].strftime('%Y-%m-%d'),
            key_levels={
                'resistance': float(resistance),
                'support': float(support),
                'target': float(target),
                'current_price': float(current_price)
            },
            volume_confirmed=False
        )
        
        self.patterns.append(pattern)
    
    def detect_descending_triangle(self):
        """
        Descending Triangle Pattern Detection
        
        Structure: Flat bottom (support) with declining highs
        Signal: Bearish continuation
        """
        if len(self.swing_highs) < 3 or len(self.swing_lows) < 3:
            return
        
        recent_data = self.df.tail(50)
        if len(recent_data) < 30:
            return
        
        # Find support level (multiple lows at same level)
        recent_lows = [price for idx, price in self.swing_lows if idx >= len(self.df) - 50]
        
        if len(recent_lows) < 3:
            return
        
        # Check if lows are relatively flat (within 1%)
        support = min(recent_lows)
        flat_lows = [l for l in recent_lows if abs(l - support) / support < 0.01]
        
        if len(flat_lows) < 2:
            return
        
        # Check if highs are descending
        recent_highs = [price for idx, price in self.swing_highs if idx >= len(self.df) - 50]
        
        if len(recent_highs) < 2:
            return
        
        if recent_highs[-1] >= recent_highs[0]:
            return
        
        resistance = max(recent_highs)
        
        current_price = self.df['close'].iloc[-1]
        if current_price < support * 0.98 or current_price > resistance:
            return
        
        # Target after breakdown = height of triangle
        height = resistance - support
        target = support - height
        
        pattern = Pattern(
            name="Descending Triangle",
            type="continuation",
            signal="bearish",
            confidence=65,
            description="Bearish continuation pattern. Flat support with declining resistance. Expect downside breakdown.",
            start_date=self.df.index[-50].strftime('%Y-%m-%d'),
            end_date=self.df.index[-1].strftime('%Y-%m-%d'),
            key_levels={
                'resistance': float(resistance),
                'support': float(support),
                'target': float(target),
                'current_price': float(current_price)
            },
            volume_confirmed=False
        )
        
        self.patterns.append(pattern)
    
    def detect_symmetric_triangle(self):
        """
        Symmetric Triangle Pattern Detection
        
        Structure: Converging trendlines (rising lows and falling highs)
        Signal: Neutral (breakout direction determines trend)
        """
        if len(self.swing_highs) < 3 or len(self.swing_lows) < 3:
            return
        
        recent_highs = [(idx, price) for idx, price in self.swing_highs if idx >= len(self.df) - 50]
        recent_lows = [(idx, price) for idx, price in self.swing_lows if idx >= len(self.df) - 50]
        
        if len(recent_highs) < 3 or len(recent_lows) < 3:
            return
        
        # Check if highs are descending
        if not (recent_highs[-1][1] < recent_highs[0][1]):
            return
        
        # Check if lows are ascending
        if not (recent_lows[-1][1] > recent_lows[0][1]):
            return
        
        # Lines should be converging
        initial_range = recent_highs[0][1] - recent_lows[0][1]
        current_range = recent_highs[-1][1] - recent_lows[-1][1]
        
        if current_range >= initial_range:
            return
        
        upper_line = recent_highs[-1][1]
        lower_line = recent_lows[-1][1]
        
        pattern = Pattern(
            name="Symmetric Triangle",
            type="continuation",
            signal="neutral",
            confidence=60,
            description="Neutral consolidation pattern. Converging trendlines. Breakout direction indicates trend.",
            start_date=self.df.index[recent_lows[0][0]].strftime('%Y-%m-%d'),
            end_date=self.df.index[-1].strftime('%Y-%m-%d'),
            key_levels={
                'upper_line': float(upper_line),
                'lower_line': float(lower_line),
                'current_price': float(self.df['close'].iloc[-1])
            },
            volume_confirmed=False
        )
        
        self.patterns.append(pattern)
    
    def detect_bull_flag(self):
        """
        Bull Flag Pattern Detection
        
        Structure: Sharp rally (flagpole) followed by downward consolidation (flag)
        Signal: Bullish continuation
        """
        # Need at least 30 bars
        if len(self.df) < 30:
            return
        
        recent_data = self.df.tail(30)
        
        # Check for sharp rally (flagpole) - at least 10% gain in 5-10 days
        flagpole_start = recent_data.iloc[0]['close']
        flagpole_end = recent_data.iloc[10]['high']
        
        flagpole_gain = (flagpole_end - flagpole_start) / flagpole_start
        
        if flagpole_gain < 0.10:  # Less than 10% gain
            return
        
        # Check for downward consolidation (flag)
        flag_data = recent_data.iloc[10:]
        
        if len(flag_data) < 10:
            return
        
        # Flag should slope slightly down or sideways
        flag_start = flag_data.iloc[0]['high']
        flag_end = flag_data.iloc[-1]['close']
        
        if flag_end > flag_start:  # Should not be rising
            return
        
        # Current price should be within flag
        current_price = self.df['close'].iloc[-1]
        
        pattern = Pattern(
            name="Bull Flag",
            type="continuation",
            signal="bullish",
            confidence=70,
            description="Bullish continuation pattern. Sharp rally followed by consolidation. Expect upside breakout.",
            start_date=recent_data.index[0].strftime('%Y-%m-%d'),
            end_date=recent_data.index[-1].strftime('%Y-%m-%d'),
            key_levels={
                'flagpole_start': float(flagpole_start),
                'flagpole_end': float(flagpole_end),
                'flag_top': float(flag_start),
                'current_price': float(current_price),
                'target': float(flagpole_end + (flagpole_end - flagpole_start))
            },
            volume_confirmed=self._check_volume_confirmation(0, 10)
        )
        
        self.patterns.append(pattern)
    
    def detect_bear_flag(self):
        """
        Bear Flag Pattern Detection
        
        Structure: Sharp decline (flagpole) followed by upward consolidation (flag)
        Signal: Bearish continuation
        """
        if len(self.df) < 30:
            return
        
        recent_data = self.df.tail(30)
        
        # Check for sharp decline (flagpole) - at least 10% drop in 5-10 days
        flagpole_start = recent_data.iloc[0]['close']
        flagpole_end = recent_data.iloc[10]['low']
        
        flagpole_drop = (flagpole_start - flagpole_end) / flagpole_start
        
        if flagpole_drop < 0.10:  # Less than 10% drop
            return
        
        # Check for upward consolidation (flag)
        flag_data = recent_data.iloc[10:]
        
        if len(flag_data) < 10:
            return
        
        # Flag should slope slightly up or sideways
        flag_start = flag_data.iloc[0]['low']
        flag_end = flag_data.iloc[-1]['close']
        
        if flag_end < flag_start:  # Should not be falling
            return
        
        current_price = self.df['close'].iloc[-1]
        
        pattern = Pattern(
            name="Bear Flag",
            type="continuation",
            signal="bearish",
            confidence=70,
            description="Bearish continuation pattern. Sharp decline followed by consolidation. Expect downside breakdown.",
            start_date=recent_data.index[0].strftime('%Y-%m-%d'),
            end_date=recent_data.index[-1].strftime('%Y-%m-%d'),
            key_levels={
                'flagpole_start': float(flagpole_start),
                'flagpole_end': float(flagpole_end),
                'flag_bottom': float(flag_start),
                'current_price': float(current_price),
                'target': float(flagpole_end - (flagpole_start - flagpole_end))
            },
            volume_confirmed=self._check_volume_confirmation(0, 10)
        )
        
        self.patterns.append(pattern)
    
    def detect_rising_wedge(self):
        """
        Rising Wedge Pattern Detection
        
        Structure: Both support and resistance rising, but converging
        Signal: Bearish (typically breakdown)
        """
        # Implementation similar to triangles but both lines rising
        # Left as exercise - can be added based on need
        pass
    
    def detect_falling_wedge(self):
        """
        Falling Wedge Pattern Detection
        
        Structure: Both support and resistance falling, but converging
        Signal: Bullish (typically breakout)
        """
        # Implementation similar to triangles but both lines falling
        pass
    
    # ==================== CANDLESTICK PATTERNS ====================
    
    def detect_doji(self):
        """
        Doji Candlestick Pattern Detection
        
        Structure: Open and close are nearly equal (small body)
        Signal: Indecision, potential reversal
        """
        # Check last 5 candles
        for i in range(max(0, len(self.df) - 5), len(self.df)):
            candle = self.df.iloc[i]
            
            body = abs(candle['close'] - candle['open'])
            full_range = candle['high'] - candle['low']
            
            # Doji: body is less than 10% of full range
            if full_range > 0 and (body / full_range) < 0.1:
                pattern = Pattern(
                    name="Doji",
                    type="candlestick",
                    signal="neutral",
                    confidence=50,
                    description="Doji candle indicates indecision. Potential reversal signal.",
                    start_date=self.df.index[i].strftime('%Y-%m-%d'),
                    end_date=self.df.index[i].strftime('%Y-%m-%d'),
                    key_levels={
                        'open': float(candle['open']),
                        'close': float(candle['close']),
                        'high': float(candle['high']),
                        'low': float(candle['low'])
                    },
                    volume_confirmed=False
                )
                
                self.patterns.append(pattern)
    
    def detect_hammer(self):
        """
        Hammer Candlestick Pattern Detection
        
        Structure: Small body at top, long lower shadow (2x body)
        Signal: Bullish reversal (after downtrend)
        """
        if len(self.df) < 2:
            return
        
        candle = self.df.iloc[-1]
        prev_candle = self.df.iloc[-2]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        # Hammer criteria:
        # 1. Lower shadow at least 2x body
        # 2. Little or no upper shadow
        # 3. Appears after downtrend
        
        if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.3:
            # Check if in downtrend
            if prev_candle['close'] < self.df.iloc[-10]['close']:
                pattern = Pattern(
                    name="Hammer",
                    type="candlestick",
                    signal="bullish",
                    confidence=65,
                    description="Hammer candle after downtrend. Bullish reversal signal.",
                    start_date=self.df.index[-1].strftime('%Y-%m-%d'),
                    end_date=self.df.index[-1].strftime('%Y-%m-%d'),
                    key_levels={
                        'low': float(candle['low']),
                        'close': float(candle['close']),
                        'support': float(candle['low'])
                    },
                    volume_confirmed=False
                )
                
                self.patterns.append(pattern)
    
    def detect_shooting_star(self):
        """
        Shooting Star Candlestick Pattern Detection
        
        Structure: Small body at bottom, long upper shadow (2x body)
        Signal: Bearish reversal (after uptrend)
        """
        if len(self.df) < 2:
            return
        
        candle = self.df.iloc[-1]
        prev_candle = self.df.iloc[-2]
        
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        # Shooting star criteria:
        # 1. Upper shadow at least 2x body
        # 2. Little or no lower shadow
        # 3. Appears after uptrend
        
        if body > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.3:
            # Check if in uptrend
            if prev_candle['close'] > self.df.iloc[-10]['close']:
                pattern = Pattern(
                    name="Shooting Star",
                    type="candlestick",
                    signal="bearish",
                    confidence=65,
                    description="Shooting star candle after uptrend. Bearish reversal signal.",
                    start_date=self.df.index[-1].strftime('%Y-%m-%d'),
                    end_date=self.df.index[-1].strftime('%Y-%m-%d'),
                    key_levels={
                        'high': float(candle['high']),
                        'close': float(candle['close']),
                        'resistance': float(candle['high'])
                    },
                    volume_confirmed=False
                )
                
                self.patterns.append(pattern)
    
    def detect_engulfing(self):
        """
        Engulfing Pattern Detection (Bullish and Bearish)
        
        Structure: Current candle completely engulfs previous candle
        Signal: Reversal pattern
        """
        if len(self.df) < 2:
            return
        
        prev_candle = self.df.iloc[-2]
        curr_candle = self.df.iloc[-1]
        
        prev_body = abs(prev_candle['close'] - prev_candle['open'])
        curr_body = abs(curr_candle['close'] - curr_candle['open'])
        
        # Bullish engulfing: green candle engulfs red candle
        if (prev_candle['close'] < prev_candle['open'] and  # prev is red
            curr_candle['close'] > curr_candle['open'] and  # curr is green
            curr_candle['open'] <= prev_candle['close'] and
            curr_candle['close'] >= prev_candle['open']):
            
            pattern = Pattern(
                name="Bullish Engulfing",
                type="candlestick",
                signal="bullish",
                confidence=70,
                description="Bullish engulfing pattern. Green candle engulfs previous red candle. Reversal signal.",
                start_date=self.df.index[-2].strftime('%Y-%m-%d'),
                end_date=self.df.index[-1].strftime('%Y-%m-%d'),
                key_levels={
                    'support': float(curr_candle['low']),
                    'close': float(curr_candle['close'])
                },
                volume_confirmed=curr_candle['volume'] > prev_candle['volume']
            )
            
            self.patterns.append(pattern)
        
        # Bearish engulfing: red candle engulfs green candle
        elif (prev_candle['close'] > prev_candle['open'] and  # prev is green
              curr_candle['close'] < curr_candle['open'] and  # curr is red
              curr_candle['open'] >= prev_candle['close'] and
              curr_candle['close'] <= prev_candle['open']):
            
            pattern = Pattern(
                name="Bearish Engulfing",
                type="candlestick",
                signal="bearish",
                confidence=70,
                description="Bearish engulfing pattern. Red candle engulfs previous green candle. Reversal signal.",
                start_date=self.df.index[-2].strftime('%Y-%m-%d'),
                end_date=self.df.index[-1].strftime('%Y-%m-%d'),
                key_levels={
                    'resistance': float(curr_candle['high']),
                    'close': float(curr_candle['close'])
                },
                volume_confirmed=curr_candle['volume'] > prev_candle['volume']
            )
            
            self.patterns.append(pattern)
    
    def get_pattern_summary(self) -> Dict:
        """Return summary of detected patterns"""
        return {
            'total_patterns': len(self.patterns),
            'bullish': len([p for p in self.patterns if p.signal == 'bullish']),
            'bearish': len([p for p in self.patterns if p.signal == 'bearish']),
            'neutral': len([p for p in self.patterns if p.signal == 'neutral']),
            'high_confidence': len([p for p in self.patterns if p.confidence >= 70]),
            'patterns': [
                {
                    'name': p.name,
                    'type': p.type,
                    'signal': p.signal,
                    'confidence': int(p.confidence),
                    'description': p.description,
                    'start_date': p.start_date,
                    'end_date': p.end_date,
                    'key_levels': {k: float(v) for k, v in p.key_levels.items()},
                    'volume_confirmed': bool(p.volume_confirmed)  # Explicitly convert to JSON-safe bool
                }
                for p in self.patterns
            ]
        }


def detect_patterns(df: pd.DataFrame) -> Dict:
    """
    Main function to detect all patterns in a DataFrame
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Dictionary with pattern summary and list of detected patterns
    """
    detector = PatternDetector(df)
    detector.detect_all_patterns()
    return detector.get_pattern_summary()
