"""
Technical analysis endpoints - Signal generation, indicators, pattern detection.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import pandas as pd

from src.services.data.ingestion import fetch_ohlcv
from src.services.analysis.signals import generate_signals
from src.core.logging import logger
from src.core.exceptions import DataFetchError, AnalysisError
from src.core.dependencies import get_current_active_user
from src.models.user import User
from src.models.query_history import QueryHistory
from src.db.session import get_db

router = APIRouter()


class AnalysisRequest(BaseModel):
    ticker: str
    period: str = '1y'
    interval: str = '1d'


class SignalResponse(BaseModel):
    ticker: str
    signal: str
    rsi: float
    macd: float
    macd_signal: float
    current_price: float
    timestamp: str


@router.post("/signal", response_model=SignalResponse)
async def get_trading_signal(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get trading signal for a ticker based on technical indicators.
    
    - **ticker**: Stock symbol (e.g., AAPL, TSLA)
    - **period**: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
    - **interval**: Data interval (1d, 1h, 30m, etc.)
    
    Returns signal (BUY/SELL/HOLD) with indicators.
    """
    try:
        logger.info(f"Fetching signal for {request.ticker} - User: {current_user.username}")
        
        # Fetch data
        df = fetch_ohlcv(request.ticker, period=request.period, interval=request.interval)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker: {request.ticker}"
            )
        
        # Generate signals
        df = generate_signals(df)
        latest = df.iloc[-1]
        
        signal_value = latest.get('signal', 0)
        signal_text = 'BUY' if signal_value == 1 else 'SELL' if signal_value == -1 else 'HOLD'
        
        return SignalResponse(
            ticker=request.ticker,
            signal=signal_text,
            rsi=float(latest.get('rsi', 0)),
            macd=float(latest.get('macd', 0)),
            macd_signal=float(latest.get('macd_signal', 0)),
            current_price=float(latest['close']),
            timestamp=str(latest.name)
        )
        
    except DataFetchError as e:
        logger.error(f"Data fetch error for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
    except AnalysisError as e:
        logger.error(f"Analysis error for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for {request.ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/indicators/{ticker}")
async def get_indicators(
    ticker: str,
    period: str = '1y',
    interval: str = '1d',
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all technical indicators for a ticker.
    
    Returns full indicator data including RSI, MACD, moving averages.
    """
    try:
        logger.info(f"Fetching indicators for {ticker} - User: {current_user.username}")
        
        df = fetch_ohlcv(ticker, period=period, interval=interval)
        df = generate_signals(df)
        
        # Return last 100 data points
        result_df = df.tail(100)
        
        return {
            "ticker": ticker,
            "data": result_df.to_dict(orient='records'),
            "count": len(result_df)
        }
        
    except Exception as e:
        logger.error(f"Error fetching indicators for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{ticker}")
async def get_market_summary(
    ticker: str,
    period: str = '1y',
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive market summary for a ticker.
    
    Includes price statistics, volatility, trend analysis.
    """
    try:
        logger.info(f"Fetching summary for {ticker} - User: {current_user.username}")
        
        df = fetch_ohlcv(ticker, period=period)
        df = generate_signals(df)
        
        latest = df.iloc[-1]
        
        # Calculate statistics
        price_change_pct = ((latest['close'] - df.iloc[0]['close']) / df.iloc[0]['close']) * 100
        volatility = df['close'].pct_change().std() * 100
        high_52w = df['high'].max()
        low_52w = df['low'].min()
        avg_volume = df['volume'].mean()
        
        return {
            "ticker": ticker,
            "current_price": float(latest['close']),
            "price_change_pct": round(price_change_pct, 2),
            "volatility": round(volatility, 2),
            "high_52w": float(high_52w),
            "low_52w": float(low_52w),
            "avg_volume": int(avg_volume),
            "rsi": float(latest.get('rsi', 0)),
            "macd": float(latest.get('macd', 0)),
            "signal": 'BUY' if latest.get('signal', 0) == 1 else 'SELL' if latest.get('signal', 0) == -1 else 'HOLD'
        }
        
    except Exception as e:
        logger.error(f"Error fetching summary for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_query_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's query history.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    
    Returns list of past queries with results.
    """
    try:
        logger.info(f"Fetching query history for user: {current_user.username}")
        
        # Query user's history
        queries = db.query(QueryHistory).filter(
            QueryHistory.user_id == current_user.id
        ).order_by(
            QueryHistory.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Count total queries
        total = db.query(QueryHistory).filter(
            QueryHistory.user_id == current_user.id
        ).count()
        
        return {
            "queries": [
                {
                    "id": q.id,
                    "query_text": q.query_text,
                    "query_type": q.query_type,
                    "ticker": q.ticker,
                    "result": q.result,
                    "status": q.status,
                    "created_at": q.created_at.isoformat() if q.created_at else None,
                    "completed_at": q.completed_at.isoformat() if q.completed_at else None
                }
                for q in queries
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching query history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{query_id}")
async def get_single_query(
    query_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single query by ID.
    
    - **query_id**: The ID of the query to retrieve
    
    Returns the query details with results.
    """
    try:
        logger.info(f"Fetching query {query_id} for user: {current_user.username}")
        
        # Query the specific record
        query = db.query(QueryHistory).filter(
            QueryHistory.id == query_id,
            QueryHistory.user_id == current_user.id
        ).first()
        
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        
        return {
            "id": query.id,
            "query_text": query.query_text,
            "query_type": query.query_type,
            "ticker": query.ticker,
            "result": query.result,
            "status": query.status,
            "error_message": query.error_message,
            "created_at": query.created_at.isoformat() if query.created_at else None,
            "completed_at": query.completed_at.isoformat() if query.completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching query {query_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
