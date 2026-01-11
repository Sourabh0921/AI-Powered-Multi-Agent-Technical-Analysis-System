"""
Sentiment Analysis API Endpoints
RESTful API for accessing sentiment analysis features
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
from datetime import datetime

from ....sentiment.aggregator import SentimentAggregator
from ....core.config import settings
from ....core.logging import logger


router = APIRouter(prefix="/sentiment", tags=["sentiment"])


def get_sentiment_aggregator():
    """Dependency: Create SentimentAggregator instance"""
    api_keys = {
        'newsapi': getattr(settings, 'NEWSAPI_KEY', None),
        'alpha_vantage': getattr(settings, 'ALPHA_VANTAGE_KEY', None),
        'finnhub': getattr(settings, 'FINNHUB_KEY', None),
        'twitter_bearer': getattr(settings, 'TWITTER_BEARER_TOKEN', None),
        'reddit_client_id': getattr(settings, 'REDDIT_CLIENT_ID', None),
        'reddit_client_secret': getattr(settings, 'REDDIT_CLIENT_SECRET', None),
        'stocktwits': getattr(settings, 'STOCKTWITS_TOKEN', None)
    }
    return SentimentAggregator(api_keys)


@router.get("/{ticker}")
async def get_sentiment(
    ticker: str,
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get comprehensive sentiment analysis for a ticker.
    
    Includes:
    - News sentiment (NewsAPI, Alpha Vantage, Finnhub)
    - Social media sentiment (Twitter, Reddit, StockTwits)
    - SEC filings sentiment (Insider trading, material events)
    - Composite score with confidence
    
    **Example Request:**
    ```
    GET /api/v1/sentiment/AAPL
    ```
    
    **Example Response:**
    ```json
    {
        "ticker": "AAPL",
        "timestamp": "2024-01-15T10:30:00",
        "composite_score": 0.65,
        "composite_label": "Positive",
        "confidence": 0.78,
        "recommendation": "BUY",
        "sources": {
            "news": {...},
            "social": {...},
            "sec": {...}
        }
    }
    ```
    """
    try:
        logger.info(f"📊 Sentiment analysis request for {ticker}")
        
        result = aggregator.analyze_all(ticker)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No sentiment data available for {ticker}"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/quick")
async def get_quick_sentiment(
    ticker: str,
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get quick sentiment analysis (StockTwits only).
    
    Fast endpoint that returns sentiment from social media platforms
    without waiting for news or SEC data.
    
    **Use Case:** Real-time sentiment checks, streaming data
    
    **Example Request:**
    ```
    GET /api/v1/sentiment/TSLA/quick
    ```
    """
    try:
        logger.info(f"⚡ Quick sentiment request for {ticker}")
        
        result = aggregator.quick_sentiment(ticker)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'quick_sentiment': result
        }
        
    except Exception as e:
        logger.error(f"Error in quick sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def get_batch_sentiment(
    tickers: List[str],
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict[str, Dict]:
    """
    Get sentiment analysis for multiple tickers.
    
    **Request Body:**
    ```json
    {
        "tickers": ["AAPL", "GOOGL", "MSFT"]
    }
    ```
    
    **Response:**
    ```json
    {
        "AAPL": {...},
        "GOOGL": {...},
        "MSFT": {...}
    }
    ```
    
    **Rate Limits:** Maximum 10 tickers per request
    """
    if len(tickers) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tickers allowed per batch request"
        )
    
    try:
        logger.info(f"📊 Batch sentiment analysis for {len(tickers)} tickers")
        
        results = aggregator.batch_analyze(tickers)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/news")
async def get_news_sentiment(
    ticker: str,
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get news sentiment only.
    
    Returns sentiment analysis from news sources:
    - NewsAPI
    - Alpha Vantage News
    - Finnhub News
    - Yahoo Finance RSS (fallback)
    """
    try:
        logger.info(f"📰 News sentiment request for {ticker}")
        
        result = aggregator.news_analyzer.analyze(ticker)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'news_sentiment': result
        }
        
    except Exception as e:
        logger.error(f"Error in news sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/social")
async def get_social_sentiment(
    ticker: str,
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get social media sentiment only.
    
    Returns sentiment analysis from:
    - Twitter/X
    - Reddit (r/wallstreetbets, r/stocks)
    - StockTwits
    """
    try:
        logger.info(f"💬 Social sentiment request for {ticker}")
        
        result = aggregator.social_analyzer.analyze(ticker)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'social_sentiment': result
        }
        
    except Exception as e:
        logger.error(f"Error in social sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/sec")
async def get_sec_sentiment(
    ticker: str,
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get SEC filings sentiment only.
    
    Returns sentiment analysis from:
    - Form 4 (Insider Trading)
    - Form 8-K (Material Events)
    """
    try:
        logger.info(f"📄 SEC sentiment request for {ticker}")
        
        result = aggregator.sec_analyzer.analyze(ticker)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'sec_sentiment': result
        }
        
    except Exception as e:
        logger.error(f"Error in SEC sentiment for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/trending")
async def get_trending_topics(
    ticker: str,
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get trending topics and keywords for a ticker.
    
    Returns:
    - Top trending keywords from news
    - Trending tickers from social media
    - Recent insider trading activity
    """
    try:
        logger.info(f"🔥 Trending topics request for {ticker}")
        
        # Get trending keywords from news
        news_trends = aggregator.news_analyzer.get_trending_topics(ticker)
        
        # Get trending tickers from social media
        social_trends = aggregator.social_analyzer.get_trending_tickers()
        
        # Get recent Form 4 filings
        sec_filings = aggregator.sec_analyzer.get_recent_form4(ticker)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'trending_keywords': news_trends,
            'trending_tickers': social_trends,
            'recent_insider_activity': sec_filings
        }
        
    except Exception as e:
        logger.error(f"Error getting trending topics for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/overview")
async def get_market_sentiment_overview(
    tickers: Optional[List[str]] = Query(None, description="Specific tickers to analyze"),
    aggregator: SentimentAggregator = Depends(get_sentiment_aggregator)
) -> Dict:
    """
    Get market-wide sentiment overview.
    
    If tickers not provided, analyzes top trending tickers from social media.
    
    **Example:**
    ```
    GET /api/v1/sentiment/market/overview?tickers=AAPL,GOOGL,MSFT
    ```
    
    **Response:**
    ```json
    {
        "timestamp": "2024-01-15T10:30:00",
        "market_sentiment": "Bullish",
        "average_score": 0.42,
        "tickers_analyzed": 10,
        "top_positive": ["AAPL", "GOOGL"],
        "top_negative": ["XYZ"],
        "breakdown": {...}
    }
    ```
    """
    try:
        logger.info("🌍 Market sentiment overview request")
        
        # If no tickers provided, use trending tickers
        if not tickers:
            trending = aggregator.social_analyzer.get_trending_tickers()
            tickers = [t['ticker'] for t in trending[:10]]  # Top 10
        
        # Analyze all tickers
        results = aggregator.batch_analyze(tickers)
        
        # Calculate market averages
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            raise HTTPException(
                status_code=404,
                detail="No valid sentiment data available"
            )
        
        avg_score = sum(r['composite_score'] for r in valid_results.values()) / len(valid_results)
        
        # Sort by score
        sorted_results = sorted(
            valid_results.items(),
            key=lambda x: x[1]['composite_score'],
            reverse=True
        )
        
        top_positive = [ticker for ticker, _ in sorted_results[:5]]
        top_negative = [ticker for ticker, _ in sorted_results[-5:]]
        
        # Classify market sentiment
        if avg_score > 0.3:
            market_sentiment = "Bullish"
        elif avg_score > 0:
            market_sentiment = "Moderately Bullish"
        elif avg_score > -0.3:
            market_sentiment = "Moderately Bearish"
        else:
            market_sentiment = "Bearish"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'market_sentiment': market_sentiment,
            'average_score': round(avg_score, 3),
            'tickers_analyzed': len(valid_results),
            'top_positive': top_positive,
            'top_negative': top_negative,
            'breakdown': valid_results
        }
        
    except Exception as e:
        logger.error(f"Error in market sentiment overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))
