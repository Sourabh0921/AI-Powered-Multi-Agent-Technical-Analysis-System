"""
Technical Analysis Module
Analyzes technical indicators and generates technical scores
"""
from typing import Dict
import pandas as pd

from .constants import RSI_THRESHOLDS, SCORE_THRESHOLDS
from ...core.logging import logger


class TechnicalAnalyzer:
    """
    Technical Analysis Engine
    
    Analyzes:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Moving Averages (SMA 20, 50, 200)
    - Support/Resistance levels
    - Trend detection
    """
    
    def __init__(self):
        self.rsi_thresholds = RSI_THRESHOLDS
        self.score_thresholds = SCORE_THRESHOLDS['technical']
    
    def analyze(self, ticker: str, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive technical analysis
        
        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLCV data and calculated indicators
            
        Returns:
            Technical analysis result dictionary
        """
        logger.info(f"📈 Analyzing technical indicators for {ticker}")
        
        latest = df.iloc[-1]
        recent = df.tail(20)
        
        # Extract indicators
        indicators = self._extract_indicators(latest)
        
        # Calculate technical score
        tech_score, signals = self._calculate_technical_score(indicators)
        
        # Determine trend
        trend = self._determine_trend(indicators)
        
        # Calculate support and resistance
        support = float(recent['low'].min())
        resistance = float(recent['high'].max())
        
        # Normalize score to -1 to +1
        normalized_score = max(-1, min(1, tech_score / 100))
        
        return {
            'score': normalized_score,
            'label': self._classify_score(normalized_score),
            'trend': trend,
            'indicators': indicators,
            'signals': signals,
            'support': support,
            'resistance': resistance,
            'recommendation': self._get_recommendation(normalized_score)
        }
    
    def _extract_indicators(self, latest: pd.Series) -> Dict:
        """Extract technical indicators from latest data point"""
        return {
            'rsi': latest.get('rsi', 50),
            'macd': latest.get('macd', 0),
            'macd_signal': latest.get('macd_signal', 0),
            'sma_20': latest.get('sma_20', 0),
            'sma_50': latest.get('sma_50', 0),
            'sma_200': latest.get('sma_200', 0),
            'volume': latest.get('volume', 0),
            'close': latest.get('close', 0)
        }
    
    def _calculate_technical_score(self, indicators: Dict) -> tuple[float, list]:
        """
        Calculate technical score based on indicators
        
        Returns:
            Tuple of (score, signals_list)
        """
        tech_score = 0
        signals = []
        
        # RSI analysis
        rsi = indicators['rsi']
        if rsi > self.rsi_thresholds['overbought']:
            tech_score -= 20
            signals.append("RSI Overbought (Bearish)")
        elif rsi < self.rsi_thresholds['oversold']:
            tech_score += 20
            signals.append("RSI Oversold (Bullish)")
        elif self.rsi_thresholds['neutral_low'] <= rsi <= self.rsi_thresholds['neutral_high']:
            tech_score += 5
            signals.append("RSI Neutral (Positive)")
        
        # MACD analysis
        if indicators['macd'] > indicators['macd_signal']:
            tech_score += 15
            signals.append("MACD Bullish Crossover")
        else:
            tech_score -= 10
            signals.append("MACD Bearish")
        
        # Moving Average analysis
        price = indicators['close']
        if price > indicators['sma_200']:
            tech_score += 25
            signals.append("Above 200 SMA (Strong Bullish)")
        elif price > indicators['sma_50']:
            tech_score += 15
            signals.append("Above 50 SMA (Bullish)")
        elif price > indicators['sma_20']:
            tech_score += 5
            signals.append("Above 20 SMA (Moderate Bullish)")
        else:
            tech_score -= 15
            signals.append("Below Major SMAs (Bearish)")
        
        # Golden/Death Cross
        if indicators['sma_50'] > indicators['sma_200']:
            tech_score += 20
            signals.append("Golden Cross (Very Bullish)")
        elif indicators['sma_50'] < indicators['sma_200']:
            tech_score -= 20
            signals.append("Death Cross (Very Bearish)")
        
        return tech_score, signals
    
    def _determine_trend(self, indicators: Dict) -> str:
        """Determine market trend based on moving averages"""
        price = indicators['close']
        sma_20 = indicators['sma_20']
        sma_50 = indicators['sma_50']
        sma_200 = indicators['sma_200']
        
        if price > sma_50 and sma_50 > sma_200:
            return "Strong Uptrend"
        elif price > sma_20:
            return "Uptrend"
        elif price < sma_50 and sma_50 < sma_200:
            return "Strong Downtrend"
        elif price < sma_20:
            return "Downtrend"
        else:
            return "Sideways"
    
    def _classify_score(self, score: float) -> str:
        """Classify technical score into label"""
        if score > self.score_thresholds['very_bullish']:
            return "Very Bullish"
        elif score > self.score_thresholds['bullish']:
            return "Bullish"
        elif score > self.score_thresholds['neutral_high']:
            return "Neutral"
        elif score > self.score_thresholds['bearish']:
            return "Bearish"
        else:
            return "Very Bearish"
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on technical score"""
        if score > 0.3:
            return 'BUY'
        elif score < -0.3:
            return 'SELL'
        else:
            return 'HOLD'
