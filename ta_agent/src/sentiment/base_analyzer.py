"""
Base sentiment analyzer with common NLP functionality
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Union
from enum import Enum

from ..core.logging import logger


class SentimentLabel(str, Enum):
    """Sentiment classification labels"""
    VERY_POSITIVE = "Very Positive"
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"
    VERY_NEGATIVE = "Very Negative"


@dataclass
class SentimentScore:
    """Standardized sentiment score object"""
    ticker: str
    source: str  # 'news', 'twitter', 'reddit', 'sec', 'earnings'
    score: float  # -1.0 to +1.0
    label: SentimentLabel
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    num_samples: int
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ticker': self.ticker,
            'source': self.source,
            'score': round(self.score, 3),
            'label': self.label.value,
            'confidence': round(self.confidence, 3),
            'timestamp': self.timestamp.isoformat(),
            'num_samples': self.num_samples,
            'metadata': self.metadata or {}
        }
    
    @property
    def is_bullish(self) -> bool:
        """Check if sentiment is bullish"""
        return self.score > 0.1
    
    @property
    def is_bearish(self) -> bool:
        """Check if sentiment is bearish"""
        return self.score < -0.1
    
    @property
    def strength(self) -> str:
        """Get sentiment strength description"""
        abs_score = abs(self.score)
        if abs_score > 0.6:
            return "Strong"
        elif abs_score > 0.3:
            return "Moderate"
        else:
            return "Weak"


class BaseSentimentAnalyzer(ABC):
    """
    Abstract base class for sentiment analyzers.
    All sentiment analyzers should inherit from this.
    """
    
    def __init__(self):
        self.source_name = self.__class__.__name__
        logger.info(f"Initialized {self.source_name}")
    
    @abstractmethod
    def analyze(self, ticker: str, **kwargs) -> SentimentScore:
        """
        Analyze sentiment for a ticker.
        Must be implemented by subclasses.
        """
        pass
    
    def classify_score(self, score: float) -> SentimentLabel:
        """
        Classify numerical score into sentiment label.
        
        Args:
            score: Sentiment score from -1.0 to +1.0
            
        Returns:
            SentimentLabel enum
        """
        if score > 0.4:
            return SentimentLabel.VERY_POSITIVE
        elif score > 0.15:
            return SentimentLabel.POSITIVE
        elif score > -0.15:
            return SentimentLabel.NEUTRAL
        elif score > -0.4:
            return SentimentLabel.NEGATIVE
        else:
            return SentimentLabel.VERY_NEGATIVE
    
    def normalize_score(self, raw_score: float, min_val: float, max_val: float) -> float:
        """
        Normalize a score to -1.0 to +1.0 range.
        
        Args:
            raw_score: Original score
            min_val: Minimum possible value
            max_val: Maximum possible value
            
        Returns:
            Normalized score between -1.0 and +1.0
        """
        if max_val == min_val:
            return 0.0
        
        # Normalize to 0-1
        normalized = (raw_score - min_val) / (max_val - min_val)
        
        # Convert to -1 to +1
        return (normalized * 2) - 1
    
    def calculate_confidence(self, num_samples: int, variance: float = None) -> float:
        """
        Calculate confidence score based on sample size and variance.
        
        Args:
            num_samples: Number of data points analyzed
            variance: Optional variance in the data
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from sample size
        if num_samples == 0:
            return 0.0
        elif num_samples < 5:
            base_confidence = 0.3
        elif num_samples < 20:
            base_confidence = 0.6
        elif num_samples < 50:
            base_confidence = 0.8
        else:
            base_confidence = 0.95
        
        # Adjust for variance if provided
        if variance is not None:
            variance_penalty = min(variance, 0.3)  # Max 30% penalty
            base_confidence *= (1 - variance_penalty)
        
        return min(base_confidence, 1.0)
    
    def filter_by_recency(
        self, 
        items: List[Dict], 
        timestamp_key: str = 'timestamp',
        hours: int = 24
    ) -> List[Dict]:
        """
        Filter items by recency.
        
        Args:
            items: List of items with timestamps
            timestamp_key: Key name for timestamp field
            hours: Number of hours to look back
            
        Returns:
            Filtered list of recent items
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        filtered = []
        for item in items:
            timestamp = item.get(timestamp_key)
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if timestamp and timestamp > cutoff:
                filtered.append(item)
        
        return filtered
    
    def weighted_average(
        self, 
        scores: List[float], 
        weights: Optional[List[float]] = None
    ) -> float:
        """
        Calculate weighted average of scores.
        
        Args:
            scores: List of sentiment scores
            weights: Optional list of weights (default: equal weights)
            
        Returns:
            Weighted average score
        """
        if not scores:
            return 0.0
        
        if weights is None:
            weights = [1.0] * len(scores)
        
        if len(scores) != len(weights):
            raise ValueError("Scores and weights must have same length")
        
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        return weighted_sum / total_weight


class TextSentimentProcessor:
    """
    Utility class for text-based sentiment analysis using TextBlob.
    Lightweight alternative when advanced NLP is not needed.
    """
    
    def __init__(self):
        try:
            from textblob import TextBlob
            self.TextBlob = TextBlob
            self.available = True
        except ImportError:
            logger.warning("TextBlob not available. Install with: pip install textblob")
            self.available = False
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with 'polarity' (-1 to 1) and 'subjectivity' (0 to 1)
        """
        if not self.available:
            return {'polarity': 0.0, 'subjectivity': 0.5}
        
        try:
            blob = self.TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.5}
    
    def extract_key_phrases(self, text: str, top_n: int = 10) -> List[str]:
        """Extract key noun phrases from text"""
        if not self.available:
            return []
        
        try:
            blob = self.TextBlob(text)
            phrases = list(blob.noun_phrases)
            return phrases[:top_n]
        except Exception as e:
            logger.error(f"Error extracting phrases: {e}")
            return []
