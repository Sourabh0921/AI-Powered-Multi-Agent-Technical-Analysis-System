"""
Sentiment Analysis Module for TA-Agent
Provides multi-source sentiment analysis for stocks
"""

from .base_analyzer import BaseSentimentAnalyzer, SentimentScore
from .news_analyzer import NewsAnalyzer
from .social_analyzer import SocialMediaAnalyzer
from .sec_analyzer import SECFilingsAnalyzer
from .aggregator import SentimentAggregator

__all__ = [
    'BaseSentimentAnalyzer',
    'SentimentScore',
    'NewsAnalyzer',
    'SocialMediaAnalyzer',
    'SECFilingsAnalyzer',
    'SentimentAggregator'
]
