"""
AI-powered analysis endpoints - LLM insights, workflows, autonomous agents.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import pandas as pd

from src.services.data.ingestion import fetch_ohlcv
from src.services.analysis.signals import generate_signals
from src.ai_agent.analyzers import LLMMarketAnalyzer
from src.ai_agent.workflow import TAWorkflow
from src.ai_agent.agents import AutonomousTAAgent
from src.core.logging import logger
from src.core.config import settings
from src.core.dependencies import get_current_active_user, get_db
from src.core.exceptions import AIServiceError
from src.models.user import User
from src.models.query_history import QueryHistory

router = APIRouter()


# Lazy load AI components
llm_analyzer = None
ta_workflow = None
autonomous_agent = None


def get_llm_analyzer():
    global llm_analyzer
    if llm_analyzer is None:
        llm_analyzer = LLMMarketAnalyzer()
    return llm_analyzer


def get_ta_workflow():
    global ta_workflow
    if ta_workflow is None:
        ta_workflow = TAWorkflow()
    return ta_workflow


def get_autonomous_agent():
    global autonomous_agent
    if autonomous_agent is None:
        autonomous_agent = AutonomousTAAgent()
    return autonomous_agent


class AIAnalysisRequest(BaseModel):
    query_text: Optional[str] = None
    ticker: str
    period: str = '1y'
    risk_tolerance: str = 'moderate'


class QueryRequest(BaseModel):
    query: str


@router.post("/analyze")
async def ai_market_analysis(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered market analysis using LLM.
    
    - **ticker**: Stock symbol
    - **period**: Time period for analysis
    - **risk_tolerance**: low, moderate, high
    
    Returns natural language insights and recommendations.
    """
    if not settings.ENABLE_AI:
        raise HTTPException(status_code=503, detail="AI features are disabled")
    
    # Create query history entry with user's actual question
    # Use user's question if provided, otherwise create descriptive text
    if request.query_text and request.query_text.strip():
        query_text = request.query_text.strip()
    else:
        query_text = f"Analyze {request.ticker} - {request.period} - {request.risk_tolerance} risk"
    
    query_entry = QueryHistory(
        user_id=current_user.id,
        query_text=query_text,
        query_type="ai_analysis",
        ticker=request.ticker,
        status="pending"
    )
    db.add(query_entry)
    db.commit()
    db.refresh(query_entry)
    
    try:
        logger.info(f"AI analysis for {request.ticker} - User: {current_user.username}")
        
        # Fetch and analyze data
        df = fetch_ohlcv(request.ticker, period=request.period)
        df = generate_signals(df)
        
        # Get AI analysis
        analyzer = get_llm_analyzer()
        analysis = analyzer.analyze_market_data(df, request.ticker)
        
        # Get latest metrics
        latest = df.iloc[-1]
        
        # Detect patterns
        from src.indicators.indicators import detect_patterns
        patterns = detect_patterns(df)
        
        # Prepare historical data for charts (last 90 days or available data)
        chart_data = df.tail(90).copy()
        price_data = [
            {
                "date": idx.strftime('%Y-%m-%d'),
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume']) if 'volume' in row else 0
            }
            for idx, row in chart_data.iterrows()
        ]
        
        # Prepare indicator data with all indicators
        indicator_data = [
            {
                "date": idx.strftime('%Y-%m-%d'),
                "rsi": float(row.get('rsi', 0)) if not pd.isna(row.get('rsi', 0)) else None,
                "macd": float(row.get('macd', 0)) if not pd.isna(row.get('macd', 0)) else None,
                "macd_signal": float(row.get('macd_signal', 0)) if not pd.isna(row.get('macd_signal', 0)) else None,
                "macd_hist": float(row.get('macd_hist', 0)) if not pd.isna(row.get('macd_hist', 0)) else None,
                "sma_20": float(row.get('sma_20', 0)) if not pd.isna(row.get('sma_20', 0)) else None,
                "sma_50": float(row.get('sma_50', 0)) if not pd.isna(row.get('sma_50', 0)) else None,
                "sma_200": float(row.get('sma_200', 0)) if not pd.isna(row.get('sma_200', 0)) else None,
                "ema_12": float(row.get('ema_12', 0)) if not pd.isna(row.get('ema_12', 0)) else None,
                "ema_26": float(row.get('ema_26', 0)) if not pd.isna(row.get('ema_26', 0)) else None,
                "bb_upper": float(row.get('bb_upper', 0)) if not pd.isna(row.get('bb_upper', 0)) else None,
                "bb_middle": float(row.get('bb_middle', 0)) if not pd.isna(row.get('bb_middle', 0)) else None,
                "bb_lower": float(row.get('bb_lower', 0)) if not pd.isna(row.get('bb_lower', 0)) else None,
            }
            for idx, row in chart_data.iterrows()
        ]
        
        # Prepare result with chart data
        result = {
            "ticker": request.ticker,
            "analysis": analysis,
            "risk_tolerance": request.risk_tolerance,
            "latest_price": float(latest['close']),
            "rsi": float(latest.get('rsi', 0)),
            "macd": float(latest.get('macd', 0)),
            "signal": "BUY" if latest.get('signal', 0) == 1 else "SELL" if latest.get('signal', 0) == -1 else "HOLD",
            "price_data": price_data,
            "indicator_data": indicator_data,
            "patterns": patterns
        }
        
        # Update query history with result
        query_entry.result = result
        query_entry.status = "completed"
        query_entry.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(query_entry)
        
        # Return query history object
        return {
            "id": query_entry.id,
            "query_text": query_entry.query_text,
            "query_type": query_entry.query_type,
            "ticker": query_entry.ticker,
            "result": query_entry.result,
            "status": query_entry.status,
            "created_at": query_entry.created_at.isoformat() if query_entry.created_at else None,
            "completed_at": query_entry.completed_at.isoformat() if query_entry.completed_at else None
        }
        
    except AIServiceError as e:
        logger.error(f"AI service error for {request.ticker}: {str(e)}")
        # Update query history with error
        query_entry.status = "failed"
        query_entry.error_message = str(e)
        query_entry.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Error in AI analysis for {request.ticker}: {str(e)}")
        # Update query history with error
        query_entry.status = "failed"
        query_entry.error_message = str(e)
        query_entry.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))


class ComparisonRequest(BaseModel):
    tickers: list[str]
    period: str = '6mo'


@router.post("/compare")
async def compare_stocks(
    request: ComparisonRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Compare multiple stocks side-by-side.
    
    - **tickers**: List of stock symbols (2-5 stocks)
    - **period**: Time period for comparison
    
    Returns comparative metrics and charts data for multiple stocks.
    """
    if not settings.ENABLE_AI:
        raise HTTPException(status_code=503, detail="AI features are disabled")
    
    if len(request.tickers) < 2 or len(request.tickers) > 5:
        raise HTTPException(status_code=400, detail="Please provide 2-5 tickers for comparison")
    
    try:
        logger.info(f"Comparing stocks: {request.tickers} - User: {current_user.username}")
        
        comparison_data = []
        
        for ticker in request.tickers:
            try:
                # Fetch and analyze data
                df = fetch_ohlcv(ticker, period=request.period)
                df = generate_signals(df)
                
                # Get latest metrics
                latest = df.iloc[-1]
                
                # Calculate performance
                first_price = df.iloc[0]['close']
                last_price = df.iloc[-1]['close']
                performance = ((last_price - first_price) / first_price) * 100
                
                # Prepare price data (last 90 days)
                chart_data = df.tail(90).copy()
                price_data = [
                    {
                        "date": idx.strftime('%Y-%m-%d'),
                        "close": float(row['close']),
                    }
                    for idx, row in chart_data.iterrows()
                ]
                
                comparison_data.append({
                    "ticker": ticker,
                    "current_price": float(latest['close']),
                    "performance": float(performance),
                    "rsi": float(latest.get('rsi', 0)),
                    "macd": float(latest.get('macd', 0)),
                    "signal": "BUY" if latest.get('signal', 0) == 1 else "SELL" if latest.get('signal', 0) == -1 else "HOLD",
                    "price_data": price_data,
                })
                
            except Exception as e:
                logger.warning(f"Error fetching data for {ticker}: {str(e)}")
                comparison_data.append({
                    "ticker": ticker,
                    "error": str(e)
                })
        
        return {
            "comparison": comparison_data,
            "period": request.period
        }
        
    except Exception as e:
        logger.error(f"Error in stock comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow")
async def ai_workflow_analysis(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Run multi-agent LangGraph workflow for comprehensive analysis.
    
    Executes technical, sentiment, and risk analysis agents.
    """
    if not settings.ENABLE_AI:
        raise HTTPException(status_code=503, detail="AI features are disabled")
    
    try:
        logger.info(f"AI workflow for {request.ticker} - User: {current_user.username}")
        
        # Fetch data
        df = fetch_ohlcv(request.ticker, period=request.period)
        df = generate_signals(df)
        
        # Run workflow
        workflow = get_ta_workflow()
        result = workflow.analyze(request.ticker, df)
        
        return {
            "ticker": request.ticker,
            "workflow_result": result
        }
        
    except Exception as e:
        logger.error(f"Error in AI workflow for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/query")
async def query_autonomous_agent(
    request: QueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Query the autonomous AI agent with natural language.
    
    - **query**: Natural language question about stocks/trading
    
    Example: "Should I buy AAPL right now?" or "Compare TSLA and NVDA"
    """
    if not settings.ENABLE_AI:
        raise HTTPException(status_code=503, detail="AI features are disabled")
    
    try:
        logger.info(f"Agent query: '{request.query[:50]}...' - User: {current_user.username}")
        
        agent = get_autonomous_agent()
        response = agent.analyze(request.query)
        
        return {
            "query": request.query,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error in agent query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy")
async def generate_trading_strategy(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate AI-powered trading strategy.
    
    Creates detailed entry, exit, and risk management strategies.
    """
    if not settings.ENABLE_AI:
        raise HTTPException(status_code=503, detail="AI features are disabled")
    
    try:
        logger.info(f"Strategy generation for {request.ticker} - User: {current_user.username}")
        
        # Fetch and analyze data
        df = fetch_ohlcv(request.ticker, period=request.period)
        df = generate_signals(df)
        
        # Get AI analysis
        analyzer = get_llm_analyzer()
        analysis = analyzer.analyze_market_data(df, request.ticker)
        
        # Generate strategy
        strategy = analyzer.generate_trading_strategy(analysis, request.risk_tolerance)
        
        return {
            "ticker": request.ticker,
            "risk_tolerance": request.risk_tolerance,
            "strategy": strategy
        }
        
    except Exception as e:
        logger.error(f"Error generating strategy for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ai_health_check():
    """
    Check AI services health status.
    """
    return {
        "ai_enabled": settings.ENABLE_AI,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "model": settings.DEFAULT_LLM_MODEL,
        "openai_key": bool(settings.OPENAI_API_KEY),
        "groq_key": bool(settings.GROQ_API_KEY),
        "status": "healthy"
    }
