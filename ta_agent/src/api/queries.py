# queries.py - Query management routes
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path
import threading
import logging
import json

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from ..db.session import get_db
from ..models.user import User
from ..models.query_history import QueryHistory
from ..schemas.query_schemas import QueryCreate, QueryResponse, QueryListResponse
from ..core.dependencies import get_current_user  # Use the correct auth dependency

router = APIRouter()  # Remove prefix - will be added when included in v1 router


def process_query_task(query_id: int, query_text: str, query_type: str, ticker: Optional[str] = None):
    """
    Background task to process the query with AI agent
    """
    from ..ai_agent.agents import AutonomousTAAgent
    from ..ai_agent.analyzers import LLMMarketAnalyzer
    from ..ingestion.fetch_data import fetch_ohlcv
    from ..signals.signals import generate_signals
    import logging
    import traceback
    
    logger = logging.getLogger("ta_agent")
    logger.info(f"🔄 Processing query {query_id}: type={query_type}, ticker={ticker}, text={query_text[:50] if query_text else 'N/A'}...")
    
    # Import SessionLocal from db module (reuses existing engine)
    from ..db.session import SessionLocal
    
    # Create new database session for this thread
    db = SessionLocal()
    
    query = None
    try:
        # Start a new transaction explicitly
        query = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
        if not query:
            logger.error(f"❌ Query {query_id} not found in database")
            db.close()
            return
        
        result_data = {}
        
        # Check query type and process accordingly
        if query_type == "analyze" and ticker:
            logger.info(f"📊 Processing stock analysis for {ticker}")
            # Stock analysis with market data
            df = fetch_ohlcv(ticker, period='6mo')
            df = generate_signals(df)
            
            # Detect chart patterns
            try:
                from ..patterns.advanced_patterns import detect_patterns
                patterns = detect_patterns(df)
                logger.info(f"🔍 Detected {patterns['total_patterns']} patterns for {ticker} (Bullish: {patterns['bullish']}, Bearish: {patterns['bearish']})")
            except Exception as pattern_error:
                logger.warning(f"⚠️ Pattern detection failed: {pattern_error}")
                patterns = {'total_patterns': 0, 'bullish': 0, 'bearish': 0, 'patterns': []}
            
            analyzer = LLMMarketAnalyzer()
            analysis = analyzer.analyze_market_data(df, ticker)
            
            latest = df.iloc[-1]
            
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
            import pandas as pd
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
            
            result_data = {
                "analysis": analysis,
                "ticker": ticker,
                "latest_price": float(latest['close']),
                "rsi": float(latest.get('rsi', 0)),
                "macd": float(latest.get('macd', 0)),
                "signal": "BUY" if latest.get('signal', 0) == 1 else "SELL" if latest.get('signal', 0) == -1 else "HOLD",
                "price_data": price_data,
                "indicator_data": indicator_data,
                "patterns": patterns['patterns'],
                "pattern_summary": {
                    "total": int(patterns['total_patterns']),
                    "bullish": int(patterns['bullish']),
                    "bearish": int(patterns['bearish']),
                    "high_confidence": int(patterns.get('high_confidence', 0))
                }
            }
            
            # Convert all booleans to JSON-serializable format
            result_data = json.loads(json.dumps(result_data, default=str))
        else:
            logger.info(f"💬 Processing general query with autonomous agent")
            # General query - no ticker required
            agent = AutonomousTAAgent()
            response = agent.analyze(query_text)
            result_data = {
                "response": response,
                "query_type": "general"
            }
        
        # Update query with results
        query.result = result_data
        query.status = "completed"
        query.completed_at = datetime.utcnow()
        
        # Explicitly flush and commit changes
        db.flush()
        db.commit()
        db.refresh(query)
        
        # Double-check that it was actually saved
        verification = db.query(QueryHistory).filter(QueryHistory.id == query_id).first()
        if verification:
            logger.info(f"✅ Query {query_id} completed successfully")
            logger.info(f"   DB Status: {verification.status}, Result exists: {verification.result is not None}")
            if verification.status != "completed":
                logger.error(f"   ⚠️  WARNING: Status in DB is '{verification.status}' not 'completed'!")
        else:
            logger.error(f"⚠️  Query {query_id} not found after commit!")
        
    except Exception as e:
        # Handle errors
        error_trace = traceback.format_exc()
        logger.error(f"❌ Error processing query {query_id}: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        
        # Rollback the session first
        db.rollback()
        
        if query:
            query.status = "failed"
            query.error_message = str(e)
            query.completed_at = datetime.utcnow()
            try:
                db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to commit error status: {commit_error}")
                db.rollback()
    finally:
        try:
            db.close()
        except Exception as close_error:
            logger.error(f"Failed to close DB session: {close_error}")


@router.post("/", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def create_query(
    query_data: QueryCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new query for AI analysis
    """
    logger = logging.getLogger("ta_agent")
    
    # Create query record
    new_query = QueryHistory(
        user_id=current_user.id,
        query_text=query_data.query_text,
        query_type=query_data.query_type,
        ticker=query_data.ticker,
        status="pending"
    )
    
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    
    logger.info(f"📝 Created query {new_query.id} - Starting background processing...")
    
    # Process query in background thread (more reliable than BackgroundTasks)
    try:
        thread = threading.Thread(
            target=process_query_task,
            args=(new_query.id, query_data.query_text, query_data.query_type, query_data.ticker),
            daemon=True
        )
        thread.start()
        logger.info(f"🚀 Background thread started for query {new_query.id}")
    except Exception as e:
        logger.error(f"❌ Failed to start background thread for query {new_query.id}: {str(e)}")
        # Update query status to failed
        new_query.status = "failed"
        new_query.error_message = f"Failed to start processing: {str(e)}"
        new_query.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(new_query)
    
    return new_query


@router.get("/", response_model=QueryListResponse)
async def get_user_queries(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all queries for current user
    """
    total = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id).count()
    
    queries = db.query(QueryHistory)\
        .filter(QueryHistory.user_id == current_user.id)\
        .order_by(desc(QueryHistory.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "total": total,
        "queries": queries
    }


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific query by ID
    """
    query = db.query(QueryHistory)\
        .filter(QueryHistory.id == query_id, QueryHistory.user_id == current_user.id)\
        .first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    return query


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_query(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a query
    """
    query = db.query(QueryHistory)\
        .filter(QueryHistory.id == query_id, QueryHistory.user_id == current_user.id)\
        .first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    db.delete(query)
    db.commit()
    
    return None
