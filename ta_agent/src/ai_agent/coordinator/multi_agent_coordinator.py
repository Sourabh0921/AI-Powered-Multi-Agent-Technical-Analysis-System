"""
Multi-Agent Coordinator (Refactored)
Main orchestrator combining Technical + Sentiment + Risk Analysis
"""
from typing import Dict, Optional, List
from datetime import datetime
import pandas as pd

from ...sentiment.aggregator import SentimentAggregator
from ...services.data.ingestion import fetch_ohlcv
from ...indicators.indicators import calculate_indicators
from ...signals.signals import generate_signals
from ...core.logging import logger

from .technical_analyzer import TechnicalAnalyzer
from .risk_analyzer import RiskAnalyzer
from .scoring import CompositeScorer
from .recommendation_engine import RecommendationEngine
from .constants import DEFAULT_WEIGHTS


class MultiAgentCoordinator:
    """
    Master coordinator that combines multiple analysis agents:
    - Technical Analysis Agent (RSI, MACD, Moving Averages)
    - Sentiment Analysis Agent (News, Social Media, SEC Filings)
    - Risk Assessment Agent (Volatility, Drawdown, Beta)
    
    Produces unified recommendation with confidence scores.
    """
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """Initialize all sub-agents and analyzers"""
        # Initialize sentiment aggregator
        self.sentiment_agent = SentimentAggregator(api_keys)
        
        # Initialize analysis modules
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.scorer = CompositeScorer()
        self.recommendation_engine = RecommendationEngine()
        
        # Default analysis weights (can be customized)
        self.analysis_weights = DEFAULT_WEIGHTS
        
        logger.info("✅ Multi-Agent Coordinator initialized with modular components")
    
    def comprehensive_analysis(
        self,
        ticker: str,
        period: str = '1y',
        include_sentiment: bool = True,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Perform comprehensive 360° analysis combining all agents.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period for technical analysis
            include_sentiment: Whether to include sentiment analysis
            custom_weights: Optional custom weights for different analyses
            
        Returns:
            Comprehensive analysis dictionary with all results
        """
        logger.info(f"🎯 Starting comprehensive analysis for {ticker}")
        
        weights = custom_weights or self.analysis_weights
        
        try:
            # 1. Fetch and prepare market data
            df = fetch_ohlcv(ticker, period=period)
            
            if df is None or df.empty:
                raise ValueError(f"No market data available for {ticker}")
            
            # Calculate indicators
            df = calculate_indicators(df)
            df = generate_signals(df)
            
            # 2. Technical Analysis
            logger.info("📈 Running technical analysis...")
            technical_analysis = self.technical_analyzer.analyze(ticker, df)
            
            # 3. Sentiment Analysis
            sentiment_analysis = None
            if include_sentiment:
                logger.info("💭 Running sentiment analysis...")
                sentiment_analysis = self.sentiment_agent.analyze_all(ticker)
            
            # 4. Risk Assessment
            logger.info("⚠️  Running risk assessment...")
            risk_analysis = self.risk_analyzer.analyze(ticker, df)
            
            # 5. Calculate Composite Score
            logger.info("🎲 Calculating composite score...")
            composite = self.scorer.calculate_composite(
                technical_analysis,
                sentiment_analysis,
                risk_analysis,
                weights
            )
            
            # 6. Generate Final Recommendation
            logger.info("💡 Generating final recommendation...")
            recommendation = self.recommendation_engine.generate_recommendation(
                ticker,
                technical_analysis,
                sentiment_analysis,
                risk_analysis,
                composite
            )
            
            # 7. Build comprehensive result
            return self._build_result(
                ticker,
                df,
                technical_analysis,
                sentiment_analysis,
                risk_analysis,
                composite,
                recommendation,
                weights
            )
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {ticker}: {e}")
            raise
    
    def _build_result(
        self,
        ticker: str,
        df: pd.DataFrame,
        technical_analysis: Dict,
        sentiment_analysis: Optional[Dict],
        risk_analysis: Dict,
        composite: Dict,
        recommendation: Dict,
        weights: Dict[str, float]
    ) -> Dict:
        """Build final comprehensive result dictionary"""
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'composite_score': composite['score'],
            'composite_label': composite['label'],
            'confidence': composite['confidence'],
            'recommendation': recommendation,
            'analyses': {
                'technical': technical_analysis,
                'sentiment': sentiment_analysis,
                'risk': risk_analysis
            },
            'weights_used': weights,
            'price_info': {
                'current': float(df['close'].iloc[-1]),
                'change_1d': float(df['close'].pct_change().iloc[-1] * 100),
                'high_52w': float(df['high'].rolling(252).max().iloc[-1]),
                'low_52w': float(df['low'].rolling(252).min().iloc[-1])
            }
        }
    
    def batch_analysis(self, tickers: List[str], **kwargs) -> Dict[str, Dict]:
        """
        Run comprehensive analysis on multiple tickers
        
        Args:
            tickers: List of ticker symbols
            **kwargs: Additional arguments passed to comprehensive_analysis
            
        Returns:
            Dictionary mapping tickers to their analysis results
        """
        logger.info(f"📊 Batch analysis for {len(tickers)} tickers")
        
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = self.comprehensive_analysis(ticker, **kwargs)
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                results[ticker] = {
                    'ticker': ticker,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
