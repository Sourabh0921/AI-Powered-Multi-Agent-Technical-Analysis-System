"""
Comprehensive Analysis API Endpoints
Combines Technical + Sentiment + Risk Analysis
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
from datetime import datetime

from ....ai_agent.coordinator import MultiAgentCoordinator
from ....core.config import settings
from ....core.logging import logger


router = APIRouter(prefix="/analysis", tags=["comprehensive-analysis"])


def get_coordinator():
    """Dependency: Create MultiAgentCoordinator instance"""
    api_keys = {
        'newsapi': getattr(settings, 'NEWSAPI_KEY', None),
        'alpha_vantage': getattr(settings, 'ALPHA_VANTAGE_KEY', None),
        'finnhub': getattr(settings, 'FINNHUB_KEY', None),
        'twitter_bearer': getattr(settings, 'TWITTER_BEARER_TOKEN', None),
        'reddit_client_id': getattr(settings, 'REDDIT_CLIENT_ID', None),
        'reddit_client_secret': getattr(settings, 'REDDIT_CLIENT_SECRET', None),
        'stocktwits': getattr(settings, 'STOCKTWITS_TOKEN', None)
    }
    return MultiAgentCoordinator(api_keys)


@router.get("/{ticker}")
async def comprehensive_analysis(
    ticker: str,
    period: str = Query('1y', description="Data period: 1mo, 3mo, 6mo, 1y, 2y, 5y"),
    include_sentiment: bool = Query(True, description="Include sentiment analysis"),
    coordinator: MultiAgentCoordinator = Depends(get_coordinator)
) -> Dict:
    """
    Get comprehensive 360° stock analysis.
    
    Combines:
    - **Technical Analysis**: RSI, MACD, Moving Averages, Trend Analysis
    - **Sentiment Analysis**: News, Social Media, SEC Filings
    - **Risk Assessment**: Volatility, Drawdown, Beta
    - **Final Recommendation**: BUY/SELL/HOLD with entry/exit points
    
    **Parameters:**
    - `ticker`: Stock ticker symbol (e.g., AAPL, GOOGL)
    - `period`: Historical data period (default: 1y)
    - `include_sentiment`: Enable/disable sentiment analysis (default: true)
    
    **Example Request:**
    ```
    GET /api/v1/analysis/AAPL?period=1y&include_sentiment=true
    ```
    
    **Example Response:**
    ```json
    {
        "ticker": "AAPL",
        "composite_score": 0.62,
        "composite_label": "Buy Signal",
        "confidence": 75.3,
        "recommendation": {
            "action": "BUY",
            "confidence": 75.3,
            "reasoning": "Positive signals with good confidence",
            "entry_strategy": {
                "target_price": 178.50,
                "stop_loss": 165.20,
                "take_profit_1": 190.00,
                "take_profit_2": 205.00,
                "risk_reward_ratio": 2.5
            },
            "position_sizing": "3-5% of portfolio"
        },
        "analyses": {
            "technical": {...},
            "sentiment": {...},
            "risk": {...}
        }
    }
    ```
    """
    try:
        logger.info(f"🎯 Comprehensive analysis request for {ticker}")
        
        result = coordinator.comprehensive_analysis(
            ticker=ticker,
            period=period,
            include_sentiment=include_sentiment
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in comprehensive analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_comprehensive_analysis(
    tickers: List[str],
    period: str = Query('1y', description="Data period"),
    include_sentiment: bool = Query(True, description="Include sentiment analysis"),
    coordinator: MultiAgentCoordinator = Depends(get_coordinator)
) -> Dict[str, Dict]:
    """
    Get comprehensive analysis for multiple tickers.
    
    **Request Body:**
    ```json
    {
        "tickers": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    }
    ```
    
    **Use Cases:**
    - Portfolio analysis
    - Sector comparison
    - Stock screening
    - Market overview
    
    **Rate Limits:** Maximum 10 tickers per request
    """
    if len(tickers) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tickers allowed per batch request"
        )
    
    try:
        logger.info(f"📊 Batch comprehensive analysis for {len(tickers)} tickers")
        
        results = {}
        for ticker in tickers:
            try:
                result = coordinator.comprehensive_analysis(
                    ticker=ticker,
                    period=period,
                    include_sentiment=include_sentiment
                )
                results[ticker] = result
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
                results[ticker] = {
                    'ticker': ticker,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/technical-only")
async def technical_analysis_only(
    ticker: str,
    period: str = Query('1y', description="Data period"),
    coordinator: MultiAgentCoordinator = Depends(get_coordinator)
) -> Dict:
    """
    Get technical analysis only (no sentiment).
    
    Faster endpoint for pure technical indicators and signals.
    
    **Returns:**
    - RSI, MACD, Moving Averages
    - Trend analysis
    - Support/Resistance levels
    - Technical signals
    """
    try:
        logger.info(f"📈 Technical analysis request for {ticker}")
        
        result = coordinator.comprehensive_analysis(
            ticker=ticker,
            period=period,
            include_sentiment=False
        )
        
        return {
            'ticker': result['ticker'],
            'timestamp': result['timestamp'],
            'technical_analysis': result['analyses']['technical'],
            'risk_analysis': result['analyses']['risk'],
            'price_info': result['price_info']
        }
        
    except Exception as e:
        logger.error(f"Error in technical analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticker}/comparison")
async def compare_with_peers(
    ticker: str,
    peers: List[str] = Query(..., description="Peer tickers to compare"),
    coordinator: MultiAgentCoordinator = Depends(get_coordinator)
) -> Dict:
    """
    Compare ticker with peer companies.
    
    **Example:**
    ```
    GET /api/v1/analysis/AAPL/comparison?peers=GOOGL&peers=MSFT&peers=META
    ```
    
    **Returns:**
    - Comparative scores
    - Relative rankings
    - Best opportunities
    """
    try:
        logger.info(f"⚖️  Comparison analysis for {ticker} vs {len(peers)} peers")
        
        all_tickers = [ticker] + peers
        
        if len(all_tickers) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 tickers (including target) allowed"
            )
        
        # Analyze all tickers
        results = {}
        for t in all_tickers:
            try:
                result = coordinator.comprehensive_analysis(t, period='1y')
                results[t] = result
            except Exception as e:
                results[t] = {'error': str(e)}
        
        # Filter valid results
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            raise HTTPException(
                status_code=404,
                detail="No valid analysis data available"
            )
        
        # Rank by composite score
        ranked = sorted(
            valid_results.items(),
            key=lambda x: x[1]['composite_score'],
            reverse=True
        )
        
        # Find target position
        target_position = next(
            (i + 1 for i, (t, _) in enumerate(ranked) if t == ticker),
            None
        )
        
        return {
            'target_ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'comparison': {
                'target_rank': target_position,
                'total_compared': len(valid_results),
                'rankings': [
                    {
                        'rank': i + 1,
                        'ticker': t,
                        'composite_score': r['composite_score'],
                        'recommendation': r['recommendation']['action'],
                        'confidence': r['confidence']
                    }
                    for i, (t, r) in enumerate(ranked)
                ],
                'best_opportunity': ranked[0][0] if ranked else None
            },
            'detailed_results': valid_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comparison analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio/analyze")
async def analyze_portfolio(
    tickers: List[str] = Query(..., description="Portfolio tickers"),
    coordinator: MultiAgentCoordinator = Depends(get_coordinator)
) -> Dict:
    """
    Analyze entire portfolio.
    
    **Example:**
    ```
    GET /api/v1/analysis/portfolio/analyze?tickers=AAPL&tickers=GOOGL&tickers=MSFT
    ```
    
    **Returns:**
    - Overall portfolio health
    - Risk distribution
    - Recommended rebalancing
    - Individual stock analysis
    """
    if len(tickers) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 tickers allowed for portfolio analysis"
        )
    
    try:
        logger.info(f"💼 Portfolio analysis for {len(tickers)} holdings")
        
        # Analyze all holdings
        results = coordinator.batch_analysis(tickers)
        
        # Filter valid results
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if not valid_results:
            raise HTTPException(
                status_code=404,
                detail="No valid analysis data available"
            )
        
        # Calculate portfolio metrics
        avg_score = sum(r['composite_score'] for r in valid_results.values()) / len(valid_results)
        avg_confidence = sum(r['confidence'] for r in valid_results.values()) / len(valid_results)
        
        # Risk distribution
        high_risk = sum(1 for r in valid_results.values() 
                       if r['analyses']['risk']['risk_level'] == 'High')
        moderate_risk = sum(1 for r in valid_results.values() 
                           if r['analyses']['risk']['risk_level'] == 'Moderate')
        low_risk = sum(1 for r in valid_results.values() 
                      if r['analyses']['risk']['risk_level'] == 'Low')
        
        # Action recommendations
        strong_buy = [t for t, r in valid_results.items() 
                     if r['recommendation']['action'] == 'STRONG BUY']
        buy = [t for t, r in valid_results.items() 
              if r['recommendation']['action'] == 'BUY']
        hold = [t for t, r in valid_results.items() 
               if r['recommendation']['action'] == 'HOLD']
        sell = [t for t, r in valid_results.items() 
               if r['recommendation']['action'] == 'SELL']
        strong_sell = [t for t, r in valid_results.items() 
                      if r['recommendation']['action'] == 'STRONG SELL']
        
        # Overall health
        if avg_score > 0.3:
            portfolio_health = "Strong"
        elif avg_score > 0:
            portfolio_health = "Good"
        elif avg_score > -0.3:
            portfolio_health = "Fair"
        else:
            portfolio_health = "Weak"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'portfolio_health': portfolio_health,
            'holdings_analyzed': len(valid_results),
            'metrics': {
                'average_composite_score': round(avg_score, 3),
                'average_confidence': round(avg_confidence, 1),
                'risk_distribution': {
                    'high': high_risk,
                    'moderate': moderate_risk,
                    'low': low_risk
                }
            },
            'recommendations': {
                'strong_buy': strong_buy,
                'buy': buy,
                'hold': hold,
                'sell': sell,
                'strong_sell': strong_sell
            },
            'suggested_actions': {
                'consider_selling': strong_sell + sell,
                'consider_buying_more': strong_buy,
                'monitor': hold
            },
            'detailed_analysis': valid_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in portfolio analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
