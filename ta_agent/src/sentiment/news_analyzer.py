"""
News Sentiment Analyzer
Integrates with NewsAPI, Alpha Vantage, and other news sources
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics

from .base_analyzer import BaseSentimentAnalyzer, SentimentScore, TextSentimentProcessor
from ..core.logging import logger
from ..core.config import settings


class NewsAnalyzer(BaseSentimentAnalyzer):
    """
    Analyzes sentiment from news articles using multiple sources.
    
    Supported Sources:
    - NewsAPI (newsapi.org)
    - Alpha Vantage News Sentiment
    - Finnhub News
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        super().__init__()
        
        # API keys from config or parameter
        self.api_keys = api_keys or {}
        self.newsapi_key = self.api_keys.get('newsapi') or getattr(settings, 'NEWSAPI_KEY', None)
        self.alpha_vantage_key = self.api_keys.get('alpha_vantage') or getattr(settings, 'ALPHA_VANTAGE_KEY', None)
        self.finnhub_key = self.api_keys.get('finnhub') or getattr(settings, 'FINNHUB_KEY', None)
        
        # Text processor for sentiment analysis
        self.text_processor = TextSentimentProcessor()
        
        # Company name mapping for better search
        self.company_names = self._load_company_names()
    
    def _load_company_names(self) -> Dict[str, str]:
        """Load ticker to company name mapping"""
        # Common mappings (can be expanded or loaded from file/API)
        return {
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'META': 'Meta',
            'NVDA': 'Nvidia',
            'JPM': 'JPMorgan',
            'V': 'Visa',
            'WMT': 'Walmart'
        }
    
    def analyze(
        self, 
        ticker: str, 
        days: int = 7,
        min_articles: int = 3
    ) -> SentimentScore:
        """
        Analyze news sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back
            min_articles: Minimum articles needed for analysis
            
        Returns:
            SentimentScore object
        """
        logger.info(f"Analyzing news sentiment for {ticker} (past {days} days)")
        
        # Collect articles from all available sources
        all_articles = []
        
        if self.newsapi_key:
            articles = self._fetch_newsapi(ticker, days)
            all_articles.extend(articles)
            logger.debug(f"NewsAPI: {len(articles)} articles")
        
        if self.alpha_vantage_key:
            articles = self._fetch_alpha_vantage(ticker)
            all_articles.extend(articles)
            logger.debug(f"Alpha Vantage: {len(articles)} articles")
        
        if self.finnhub_key:
            articles = self._fetch_finnhub(ticker, days)
            all_articles.extend(articles)
            logger.debug(f"Finnhub: {len(articles)} articles")
        
        # Fallback to free sources if no API keys
        if not all_articles:
            logger.warning(f"No API keys configured. Using fallback sources.")
            all_articles = self._fetch_free_sources(ticker, days)
        
        if len(all_articles) < min_articles:
            logger.warning(f"Only {len(all_articles)} articles found for {ticker}")
            return SentimentScore(
                ticker=ticker,
                source='news',
                score=0.0,
                label=self.classify_score(0.0),
                confidence=0.0,
                timestamp=datetime.now(),
                num_samples=len(all_articles),
                metadata={'warning': 'Insufficient data'}
            )
        
        # Analyze sentiment of articles
        sentiments = self._analyze_articles(all_articles)
        
        # Calculate aggregate score
        return self._aggregate_news_sentiment(ticker, sentiments, all_articles)
    
    def _fetch_newsapi(self, ticker: str, days: int) -> List[Dict]:
        """Fetch articles from NewsAPI"""
        if not self.newsapi_key:
            return []
        
        try:
            company_name = self.company_names.get(ticker, ticker)
            query = f"{ticker} OR {company_name}"
            
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'from': from_date,
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.newsapi_key,
                'pageSize': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            # Format articles
            formatted = []
            for article in articles:
                formatted.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'published_at': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []
    
    def _fetch_alpha_vantage(self, ticker: str) -> List[Dict]:
        """Fetch news from Alpha Vantage"""
        if not self.alpha_vantage_key:
            return []
        
        try:
            url = 'https://www.alphavantage.co/query'
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker,
                'apikey': self.alpha_vantage_key,
                'limit': 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            feed = data.get('feed', [])
            
            # Format articles with Alpha Vantage sentiment scores
            formatted = []
            for item in feed:
                # Extract ticker-specific sentiment
                ticker_sentiment = None
                for ts in item.get('ticker_sentiment', []):
                    if ts.get('ticker') == ticker:
                        ticker_sentiment = float(ts.get('ticker_sentiment_score', 0))
                        break
                
                formatted.append({
                    'title': item.get('title', ''),
                    'description': item.get('summary', ''),
                    'source': item.get('source', 'Unknown'),
                    'published_at': item.get('time_published', ''),
                    'url': item.get('url', ''),
                    'av_sentiment': ticker_sentiment  # Alpha Vantage sentiment
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return []
    
    def _fetch_finnhub(self, ticker: str, days: int) -> List[Dict]:
        """Fetch news from Finnhub"""
        if not self.finnhub_key:
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f'https://finnhub.io/api/v1/company-news'
            params = {
                'symbol': ticker,
                'from': from_date,
                'to': to_date,
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = response.json()
            
            # Format articles
            formatted = []
            for article in articles:
                formatted.append({
                    'title': article.get('headline', ''),
                    'description': article.get('summary', ''),
                    'source': article.get('source', 'Unknown'),
                    'published_at': datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                    'url': article.get('url', '')
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Finnhub error: {e}")
            return []
    
    def _fetch_free_sources(self, ticker: str, days: int) -> List[Dict]:
        """Fetch from free sources (Yahoo Finance, etc.)"""
        articles = []
        
        try:
            # Yahoo Finance RSS (free, no API key needed)
            import feedparser
            
            url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:20]:
                articles.append({
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'source': 'Yahoo Finance',
                    'published_at': entry.get('published', ''),
                    'url': entry.get('link', '')
                })
            
        except Exception as e:
            logger.error(f"Free sources error: {e}")
        
        return articles
    
    def _analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment of articles"""
        sentiments = []
        
        for article in articles:
            # Combine title and description
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            if not text.strip():
                continue
            
            # Use Alpha Vantage sentiment if available
            if 'av_sentiment' in article and article['av_sentiment'] is not None:
                sentiment = article['av_sentiment']
            else:
                # Use TextBlob for sentiment analysis
                analysis = self.text_processor.analyze_text(text)
                sentiment = analysis['polarity']
            
            # Calculate recency weight (recent news matters more)
            published_at = article.get('published_at', '')
            try:
                if published_at:
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    hours_ago = (datetime.now() - pub_date.replace(tzinfo=None)).total_hours()
                    # Weight decays with time (24h = 1.0, 168h = 0.5)
                    recency_weight = max(0.3, 1.0 - (hours_ago / 336))  # 2 weeks
                else:
                    recency_weight = 0.5
            except:
                recency_weight = 0.5
            
            sentiments.append({
                'article': article,
                'sentiment': sentiment,
                'weight': recency_weight,
                'source': article.get('source', 'Unknown')
            })
        
        return sentiments
    
    def _aggregate_news_sentiment(
        self, 
        ticker: str, 
        sentiments: List[Dict],
        articles: List[Dict]
    ) -> SentimentScore:
        """Aggregate individual sentiments into overall score"""
        
        if not sentiments:
            return SentimentScore(
                ticker=ticker,
                source='news',
                score=0.0,
                label=self.classify_score(0.0),
                confidence=0.0,
                timestamp=datetime.now(),
                num_samples=0
            )
        
        # Calculate weighted average
        scores = [s['sentiment'] for s in sentiments]
        weights = [s['weight'] for s in sentiments]
        
        weighted_score = self.weighted_average(scores, weights)
        
        # Calculate confidence based on sample size and variance
        variance = statistics.stdev(scores) if len(scores) > 1 else 0.0
        confidence = self.calculate_confidence(len(scores), variance)
        
        # Extract top stories
        top_stories = sorted(
            sentiments,
            key=lambda x: abs(x['sentiment']) * x['weight'],
            reverse=True
        )[:5]
        
        metadata = {
            'num_articles': len(articles),
            'avg_sentiment': weighted_score,
            'sentiment_range': [min(scores), max(scores)],
            'variance': variance,
            'top_stories': [
                {
                    'title': s['article']['title'],
                    'source': s['source'],
                    'sentiment': round(s['sentiment'], 3),
                    'url': s['article'].get('url', '')
                }
                for s in top_stories
            ]
        }
        
        return SentimentScore(
            ticker=ticker,
            source='news',
            score=weighted_score,
            label=self.classify_score(weighted_score),
            confidence=confidence,
            timestamp=datetime.now(),
            num_samples=len(sentiments),
            metadata=metadata
        )
    
    def get_trending_topics(self, ticker: str) -> List[str]:
        """Extract trending topics from news articles"""
        articles = []
        
        if self.newsapi_key:
            articles.extend(self._fetch_newsapi(ticker, days=3))
        
        if not articles:
            return []
        
        # Extract key phrases from all articles
        all_text = ' '.join([
            f"{a.get('title', '')} {a.get('description', '')}"
            for a in articles
        ])
        
        topics = self.text_processor.extract_key_phrases(all_text, top_n=10)
        return topics
