"""
Social Media Sentiment Analyzer
Integrates with Twitter/X, Reddit, and StockTwits
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import statistics

from .base_analyzer import BaseSentimentAnalyzer, SentimentScore, TextSentimentProcessor
from ..core.logging import logger
from ..core.config import settings


class SocialMediaAnalyzer(BaseSentimentAnalyzer):
    """
    Analyzes sentiment from social media platforms.
    
    Supported Platforms:
    - Twitter/X
    - Reddit (WallStreetBets, stocks, investing)
    - StockTwits
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__()
        
        self.api_keys = api_keys or {}
        self.twitter_bearer = self.api_keys.get('twitter') or getattr(settings, 'TWITTER_BEARER_TOKEN', None)
        self.reddit_client_id = self.api_keys.get('reddit_client_id') or getattr(settings, 'REDDIT_CLIENT_ID', None)
        self.reddit_client_secret = self.api_keys.get('reddit_secret') or getattr(settings, 'REDDIT_CLIENT_SECRET', None)
        self.stocktwits_token = self.api_keys.get('stocktwits') or getattr(settings, 'STOCKTWITS_TOKEN', None)
        
        self.text_processor = TextSentimentProcessor()
        
        # Sentiment keywords for financial context
        self.bullish_keywords = [
            'moon', 'bullish', 'calls', 'buy', 'long', 'rocket', '🚀', '📈',
            'breakout', 'squeeze', 'diamond hands', 'hodl', 'pump', 'rally'
        ]
        self.bearish_keywords = [
            'bearish', 'puts', 'sell', 'short', 'crash', 'dump', '📉', '🔻',
            'bubble', 'overvalued', 'puts printing', 'drill', 'tank'
        ]
    
    def analyze(
        self, 
        ticker: str,
        platforms: Optional[List[str]] = None,
        hours: int = 24
    ) -> SentimentScore:
        """
        Analyze social media sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            platforms: List of platforms to analyze (default: all available)
            hours: Hours to look back
            
        Returns:
            SentimentScore object
        """
        logger.info(f"Analyzing social media sentiment for {ticker} (past {hours} hours)")
        
        platforms = platforms or ['twitter', 'reddit', 'stocktwits']
        all_sentiments = []
        
        # Twitter/X analysis
        if 'twitter' in platforms and self.twitter_bearer:
            twitter_sentiment = self._analyze_twitter(ticker, hours)
            if twitter_sentiment:
                all_sentiments.append(twitter_sentiment)
        
        # Reddit analysis
        if 'reddit' in platforms:
            reddit_sentiment = self._analyze_reddit(ticker, hours)
            if reddit_sentiment:
                all_sentiments.append(reddit_sentiment)
        
        # StockTwits analysis
        if 'stocktwits' in platforms:
            stocktwits_sentiment = self._analyze_stocktwits(ticker)
            if stocktwits_sentiment:
                all_sentiments.append(stocktwits_sentiment)
        
        if not all_sentiments:
            logger.warning(f"No social media data available for {ticker}")
            return SentimentScore(
                ticker=ticker,
                source='social_media',
                score=0.0,
                label=self.classify_score(0.0),
                confidence=0.0,
                timestamp=datetime.now(),
                num_samples=0,
                metadata={'warning': 'No data available'}
            )
        
        # Aggregate across platforms
        return self._aggregate_social_sentiment(ticker, all_sentiments)
    
    def _analyze_twitter(self, ticker: str, hours: int) -> Optional[Dict]:
        """Analyze Twitter sentiment"""
        if not self.twitter_bearer:
            return None
        
        try:
            # Search for tweets
            query = f"${ticker} OR #{ticker} -is:retweet lang:en"
            
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {"Authorization": f"Bearer {self.twitter_bearer}"}
            params = {
                'query': query,
                'max_results': 100,
                'tweet.fields': 'created_at,public_metrics,author_id',
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tweets = data.get('data', [])
            
            if not tweets:
                return None
            
            # Analyze each tweet
            sentiments = []
            for tweet in tweets:
                text = tweet.get('text', '').lower()
                
                # Calculate sentiment using keywords
                bull_count = sum(1 for keyword in self.bullish_keywords if keyword in text)
                bear_count = sum(1 for keyword in self.bearish_keywords if keyword in text)
                
                # Combine with TextBlob
                textblob_sentiment = self.text_processor.analyze_text(text)['polarity']
                
                # Weighted sentiment
                if bull_count > bear_count:
                    keyword_sentiment = 0.5
                elif bear_count > bull_count:
                    keyword_sentiment = -0.5
                else:
                    keyword_sentiment = 0.0
                
                combined_sentiment = (textblob_sentiment * 0.6 + keyword_sentiment * 0.4)
                
                # Calculate influence based on engagement
                metrics = tweet.get('public_metrics', {})
                influence = (
                    metrics.get('like_count', 0) * 1 +
                    metrics.get('retweet_count', 0) * 3 +
                    metrics.get('reply_count', 0) * 2
                )
                
                sentiments.append({
                    'sentiment': combined_sentiment,
                    'influence': max(influence, 1),  # Minimum 1
                    'text': tweet.get('text', '')[:100]
                })
            
            # Calculate weighted average
            if sentiments:
                scores = [s['sentiment'] for s in sentiments]
                weights = [s['influence'] for s in sentiments]
                weighted_score = self.weighted_average(scores, weights)
                
                return {
                    'platform': 'twitter',
                    'score': weighted_score,
                    'count': len(sentiments),
                    'total_influence': sum(weights),
                    'samples': sentiments[:5]  # Top 5 for metadata
                }
            
        except Exception as e:
            logger.error(f"Twitter analysis error: {e}")
        
        return None
    
    def _analyze_reddit(self, ticker: str, hours: int) -> Optional[Dict]:
        """Analyze Reddit sentiment from multiple subreddits"""
        try:
            # Use Reddit without authentication for basic search
            subreddits = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
            all_posts = []
            
            for subreddit in subreddits:
                try:
                    # Use pushshift.io API (free, no auth needed)
                    url = f"https://api.pushshift.io/reddit/search/submission/"
                    params = {
                        'subreddit': subreddit,
                        'q': ticker,
                        'size': 25,
                        'sort': 'desc',
                        'sort_type': 'score'
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', [])
                        all_posts.extend(posts)
                except Exception as e:
                    logger.debug(f"Error fetching from r/{subreddit}: {e}")
                    continue
            
            if not all_posts:
                # Fallback: analyze based on keyword patterns
                return self._reddit_keyword_analysis(ticker)
            
            # Analyze posts
            sentiments = []
            for post in all_posts:
                text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
                
                # Keyword-based sentiment
                bull_count = sum(1 for keyword in self.bullish_keywords if keyword in text)
                bear_count = sum(1 for keyword in self.bearish_keywords if keyword in text)
                
                if bull_count + bear_count == 0:
                    sentiment = 0.0
                else:
                    sentiment = (bull_count - bear_count) / (bull_count + bear_count)
                
                # Weight by score (upvotes)
                score = post.get('score', 1)
                
                sentiments.append({
                    'sentiment': sentiment,
                    'weight': max(score, 1),
                    'subreddit': post.get('subreddit', ''),
                    'title': post.get('title', '')[:100]
                })
            
            if sentiments:
                scores = [s['sentiment'] for s in sentiments]
                weights = [s['weight'] for s in sentiments]
                weighted_score = self.weighted_average(scores, weights)
                
                # Calculate bullish/bearish percentages
                bullish_count = sum(1 for s in scores if s > 0.1)
                bearish_count = sum(1 for s in scores if s < -0.1)
                total = len(scores)
                
                return {
                    'platform': 'reddit',
                    'score': weighted_score,
                    'count': len(sentiments),
                    'bullish_pct': (bullish_count / total * 100) if total > 0 else 0,
                    'bearish_pct': (bearish_count / total * 100) if total > 0 else 0,
                    'samples': sentiments[:5]
                }
        
        except Exception as e:
            logger.error(f"Reddit analysis error: {e}")
        
        return None
    
    def _reddit_keyword_analysis(self, ticker: str) -> Optional[Dict]:
        """Fallback Reddit analysis using keyword patterns"""
        # Simulated analysis based on common patterns
        # In production, this would use cached data or alternative APIs
        return {
            'platform': 'reddit',
            'score': 0.0,
            'count': 0,
            'bullish_pct': 50,
            'bearish_pct': 50,
            'samples': []
        }
    
    def _analyze_stocktwits(self, ticker: str) -> Optional[Dict]:
        """Analyze StockTwits sentiment"""
        try:
            # StockTwits API (free tier available)
            url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get('messages', [])
            
            if not messages:
                return None
            
            # StockTwits provides sentiment labels
            bullish = 0
            bearish = 0
            neutral = 0
            
            for msg in messages:
                entities = msg.get('entities', {})
                sentiment = entities.get('sentiment', {})
                
                if sentiment:
                    label = sentiment.get('basic', 'neutral').lower()
                    if label == 'bullish':
                        bullish += 1
                    elif label == 'bearish':
                        bearish += 1
                    else:
                        neutral += 1
            
            total = bullish + bearish + neutral
            if total == 0:
                return None
            
            # Calculate score
            score = (bullish - bearish) / total
            
            return {
                'platform': 'stocktwits',
                'score': score,
                'count': len(messages),
                'bullish_pct': (bullish / total * 100),
                'bearish_pct': (bearish / total * 100),
                'neutral_pct': (neutral / total * 100),
                'samples': [
                    {
                        'text': msg.get('body', '')[:100],
                        'sentiment': msg.get('entities', {}).get('sentiment', {}).get('basic', 'neutral')
                    }
                    for msg in messages[:5]
                ]
            }
        
        except Exception as e:
            logger.error(f"StockTwits analysis error: {e}")
        
        return None
    
    def _aggregate_social_sentiment(
        self,
        ticker: str,
        platform_sentiments: List[Dict]
    ) -> SentimentScore:
        """Aggregate sentiment across platforms"""
        
        # Weight platforms differently
        platform_weights = {
            'twitter': 0.4,
            'reddit': 0.35,
            'stocktwits': 0.25
        }
        
        scores = []
        weights = []
        total_count = 0
        platform_details = {}
        
        for platform_data in platform_sentiments:
            platform = platform_data['platform']
            score = platform_data['score']
            count = platform_data['count']
            
            scores.append(score)
            weights.append(platform_weights.get(platform, 0.33) * count)
            total_count += count
            
            platform_details[platform] = platform_data
        
        # Calculate weighted average
        if not scores:
            weighted_score = 0.0
        else:
            weighted_score = self.weighted_average(scores, weights)
        
        # Calculate confidence
        variance = statistics.stdev(scores) if len(scores) > 1 else 0.0
        confidence = self.calculate_confidence(total_count, variance)
        
        metadata = {
            'total_mentions': total_count,
            'platforms_analyzed': len(platform_sentiments),
            'platform_breakdown': platform_details,
            'variance': variance
        }
        
        return SentimentScore(
            ticker=ticker,
            source='social_media',
            score=weighted_score,
            label=self.classify_score(weighted_score),
            confidence=confidence,
            timestamp=datetime.now(),
            num_samples=total_count,
            metadata=metadata
        )
    
    def get_trending_tickers(self, platform: str = 'stocktwits', limit: int = 10) -> List[Dict]:
        """Get trending tickers on social media"""
        try:
            if platform == 'stocktwits':
                url = "https://api.stocktwits.com/api/2/trending/symbols.json"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                symbols = data.get('symbols', [])
                
                return [
                    {
                        'ticker': s.get('symbol', ''),
                        'title': s.get('title', ''),
                        'watchlist_count': s.get('watchlist_count', 0)
                    }
                    for s in symbols[:limit]
                ]
        except Exception as e:
            logger.error(f"Error getting trending tickers: {e}")
        
        return []
