"""
Sentiment Aggregator
Combines sentiment from multiple sources into unified score
"""
from typing import List, Dict, Optional
from datetime import datetime
import statistics

from .base_analyzer import SentimentScore
from .news_analyzer import NewsAnalyzer
from .social_analyzer import SocialMediaAnalyzer
from .sec_analyzer import SECFilingsAnalyzer
from ..core.logging import logger


class SentimentAggregator:
    """
    Aggregates sentiment from all sources into a unified score.
    
    Combines:
    - News sentiment (35% weight)
    - Social media sentiment (30% weight)
    - SEC filings sentiment (20% weight)
    - Earnings sentiment (15% weight) [placeholder for future]
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Initialize all sentiment analyzers"""
        self.news_analyzer = NewsAnalyzer(api_keys)
        self.social_analyzer = SocialMediaAnalyzer(api_keys)
        self.sec_analyzer = SECFilingsAnalyzer()
        
        # Default weights (can be customized)
        self.weights = {
            'news': 0.35,
            'social_media': 0.30,
            'sec_filings': 0.20,
            'earnings': 0.15  # Reserved for future
        }
        
        logger.info("Sentiment Aggregator initialized")
    
    def analyze_all(
        self,
        ticker: str,
        include_news: bool = True,
        include_social: bool = True,
        include_sec: bool = True,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Analyze sentiment from all available sources.
        
        Args:
            ticker: Stock ticker symbol
            include_news: Include news sentiment
            include_social: Include social media sentiment
            include_sec: Include SEC filings sentiment
            custom_weights: Optional custom weights for each source
            
        Returns:
            Dictionary with comprehensive sentiment analysis
        """
        logger.info(f"🔍 Comprehensive sentiment analysis for {ticker}")
        
        # Use custom weights if provided
        weights = custom_weights or self.weights
        
        sentiment_scores = {}
        
        # News sentiment
        if include_news:
            try:
                news_sentiment = self.news_analyzer.analyze(ticker)
                sentiment_scores['news'] = news_sentiment
                logger.info(f"  📰 News: {news_sentiment.score:.3f} ({news_sentiment.label.value})")
            except Exception as e:
                logger.error(f"News analysis failed: {e}")
                sentiment_scores['news'] = None
        
        # Social media sentiment
        if include_social:
            try:
                social_sentiment = self.social_analyzer.analyze(ticker)
                sentiment_scores['social_media'] = social_sentiment
                logger.info(f"  📱 Social: {social_sentiment.score:.3f} ({social_sentiment.label.value})")
            except Exception as e:
                logger.error(f"Social analysis failed: {e}")
                sentiment_scores['social_media'] = None
        
        # SEC filings sentiment
        if include_sec:
            try:
                sec_sentiment = self.sec_analyzer.analyze(ticker)
                sentiment_scores['sec_filings'] = sec_sentiment
                logger.info(f"  📄 SEC: {sec_sentiment.score:.3f} ({sec_sentiment.label.value})")
            except Exception as e:
                logger.error(f"SEC analysis failed: {e}")
                sentiment_scores['sec_filings'] = None
        
        # Calculate composite score
        composite = self._calculate_composite(sentiment_scores, weights)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'composite_score': composite['score'],
            'composite_label': composite['label'],
            'confidence': composite['confidence'],
            'individual_scores': {
                k: v.to_dict() if v else None
                for k, v in sentiment_scores.items()
            },
            'weights_used': weights,
            'recommendation': self._generate_recommendation(composite),
            'summary': self._generate_summary(ticker, sentiment_scores, composite)
        }
    
    def _calculate_composite(
        self,
        sentiment_scores: Dict[str, Optional[SentimentScore]],
        weights: Dict[str, float]
    ) -> Dict:
        """Calculate weighted composite sentiment score"""
        
        scores = []
        score_weights = []
        confidences = []
        total_samples = 0
        
        for source, sentiment in sentiment_scores.items():
            if sentiment and sentiment.score is not None:
                weight = weights.get(source, 0)
                
                # Adjust weight by confidence
                adjusted_weight = weight * sentiment.confidence
                
                scores.append(sentiment.score)
                score_weights.append(adjusted_weight)
                confidences.append(sentiment.confidence)
                total_samples += sentiment.num_samples
        
        if not scores:
            return {
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0,
                'num_sources': 0
            }
        
        # Calculate weighted average
        total_weight = sum(score_weights)
        if total_weight == 0:
            composite_score = 0.0
        else:
            composite_score = sum(s * w for s, w in zip(scores, score_weights)) / total_weight
        
        # Calculate composite confidence
        avg_confidence = sum(confidences) / len(confidences)
        
        # Adjust confidence based on agreement between sources
        if len(scores) > 1:
            variance = statistics.stdev(scores)
            # High variance = lower confidence
            agreement_factor = max(0.5, 1.0 - variance)
            composite_confidence = avg_confidence * agreement_factor
        else:
            composite_confidence = avg_confidence * 0.7  # Single source = lower confidence
        
        # Classify composite score
        label = self._classify_score(composite_score)
        
        return {
            'score': composite_score,
            'label': label,
            'confidence': composite_confidence,
            'num_sources': len(scores),
            'total_samples': total_samples,
            'variance': statistics.stdev(scores) if len(scores) > 1 else 0.0
        }
    
    def _classify_score(self, score: float) -> str:
        """Classify composite score"""
        if score > 0.4:
            return "Very Positive 🟢"
        elif score > 0.15:
            return "Positive 🟢"
        elif score > -0.15:
            return "Neutral ⚪"
        elif score > -0.4:
            return "Negative 🔴"
        else:
            return "Very Negative 🔴"
    
    def _generate_recommendation(self, composite: Dict) -> str:
        """Generate trading recommendation based on sentiment"""
        score = composite['score']
        confidence = composite['confidence']
        
        if confidence < 0.3:
            return "INSUFFICIENT DATA - Wait for more signals"
        
        if score > 0.3 and confidence > 0.6:
            return "STRONG BUY - Positive sentiment across sources"
        elif score > 0.15 and confidence > 0.5:
            return "BUY - Moderately positive sentiment"
        elif score < -0.3 and confidence > 0.6:
            return "STRONG SELL - Negative sentiment across sources"
        elif score < -0.15 and confidence > 0.5:
            return "SELL - Moderately negative sentiment"
        else:
            return "HOLD - Mixed or neutral sentiment"
    
    def _generate_summary(
        self,
        ticker: str,
        sentiment_scores: Dict[str, Optional[SentimentScore]],
        composite: Dict
    ) -> str:
        """Generate human-readable summary"""
        
        summary_parts = [f"Sentiment Analysis for {ticker}:"]
        
        # Individual source summaries
        for source, sentiment in sentiment_scores.items():
            if sentiment:
                emoji = "🟢" if sentiment.is_bullish else "🔴" if sentiment.is_bearish else "⚪"
                summary_parts.append(
                    f"  {source.replace('_', ' ').title()}: {sentiment.label.value} {emoji} "
                    f"(score: {sentiment.score:.2f}, confidence: {sentiment.confidence:.0%})"
                )
        
        # Composite summary
        summary_parts.append(f"\nComposite Sentiment: {composite['label']}")
        summary_parts.append(f"Overall Score: {composite['score']:.3f}")
        summary_parts.append(f"Confidence: {composite['confidence']:.0%}")
        summary_parts.append(f"Sources Analyzed: {composite['num_sources']}")
        
        return "\n".join(summary_parts)
    
    def quick_sentiment(self, ticker: str) -> Dict:
        """
        Quick sentiment check using fastest sources.
        Optimized for speed over comprehensiveness.
        """
        logger.info(f"⚡ Quick sentiment check for {ticker}")
        
        # Only use StockTwits and Yahoo Finance (fastest)
        try:
            social_sentiment = self.social_analyzer.analyze(ticker, platforms=['stocktwits'], hours=12)
            
            return {
                'ticker': ticker,
                'score': social_sentiment.score,
                'label': social_sentiment.label.value,
                'confidence': social_sentiment.confidence,
                'source': 'quick_check',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Quick sentiment failed: {e}")
            return {
                'ticker': ticker,
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def batch_analyze(self, tickers: List[str]) -> Dict[str, Dict]:
        """Analyze sentiment for multiple tickers"""
        logger.info(f"📊 Batch sentiment analysis for {len(tickers)} tickers")
        
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = self.analyze_all(ticker)
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                results[ticker] = {'error': str(e)}
        
        return results
    
    def get_sentiment_strength(self, score: float) -> str:
        """Get sentiment strength description"""
        abs_score = abs(score)
        if abs_score > 0.6:
            return "Strong"
        elif abs_score > 0.3:
            return "Moderate"
        elif abs_score > 0.1:
            return "Weak"
        else:
            return "Neutral"
