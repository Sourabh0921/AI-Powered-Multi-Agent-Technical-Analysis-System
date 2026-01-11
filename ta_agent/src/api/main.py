# main.py
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from ..ingestion.fetch_data import fetch_ohlcv
from ..signals.signals import generate_signals
from ..db.db import init_db

# Import routers
from .auth import router as auth_router
from .queries import router as queries_router
from .rag_routes import router as rag_router

app = FastAPI(
    title="TA-Agent API", 
    description="AI-Powered Technical Analysis API with RAG Document QnA",
    version="2.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")

# Include routers
app.include_router(auth_router)
app.include_router(queries_router)
app.include_router(rag_router)  # RAG document QnA endpoints

# Lazy load AI components
llm_analyzer = None
ta_workflow = None
autonomous_agent = None

def get_llm_analyzer():
    global llm_analyzer
    if llm_analyzer is None:
        from ..ai_agent.analyzers import LLMMarketAnalyzer
        llm_analyzer = LLMMarketAnalyzer()
    return llm_analyzer

def get_ta_workflow():
    global ta_workflow
    if ta_workflow is None:
        from ..ai_agent.workflow import TAWorkflow
        ta_workflow = TAWorkflow()
    return ta_workflow

def get_autonomous_agent():
    global autonomous_agent
    if autonomous_agent is None:
        from ..ai_agent.agents import AutonomousTAAgent
        autonomous_agent = AutonomousTAAgent()
    return autonomous_agent


class AnalysisRequest(BaseModel):
    ticker: str
    period: str = '1y'
    risk_tolerance: str = 'moderate'

class QueryRequest(BaseModel):
    query: str


@app.get('/')
async def root():
    return {
        'message': 'TA-Agent API',
        'endpoints': [
            '/signal/{ticker}',
            '/ai/analyze',
            '/ai/workflow',
            '/ai/agent/query',
            '/ai/strategy'
        ]
    }

@app.get('/signal/{ticker}')
async def get_signal(ticker: str, period: str = '1y'):
    """Get basic technical signal"""
    try:
        df = fetch_ohlcv(ticker, period=period)
        df = generate_signals(df)
        latest = df.iloc[-1]
        return {
            'ticker': ticker,
            'date': str(df.index[-1].date()),
            'price': float(latest['close']),
            'signal': int(latest['signal']),
            'rsi': float(latest['rsi']),
            'macd': float(latest['macd']),
            'macd_hist': float(latest['macd_hist'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/ai/analyze')
async def ai_analyze(request: AnalysisRequest):
    """AI-powered market analysis using LLM"""
    if not os.getenv('GROQ_API_KEY'):
        raise HTTPException(status_code=400, detail='GROQ_API_KEY not set')
    
    try:
        df = fetch_ohlcv(request.ticker, period=request.period)
        df = generate_signals(df)
        
        analyzer = get_llm_analyzer()
        analysis = analyzer.analyze_market_data(df, request.ticker)
        
        return {
            'ticker': request.ticker,
            'analysis': analysis,
            'timestamp': str(df.index[-1])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/ai/strategy')
async def generate_strategy(request: AnalysisRequest):
    """Generate trading strategy using AI"""
    if not os.getenv('GROQ_API_KEY'):
        raise HTTPException(status_code=400, detail='GROQ_API_KEY not set')
    
    try:
        df = fetch_ohlcv(request.ticker, period=request.period)
        df = generate_signals(df)
        
        analyzer = get_llm_analyzer()
        analysis = analyzer.analyze_market_data(df, request.ticker)
        strategy = analyzer.generate_trading_strategy(analysis, request.risk_tolerance)
        
        return {
            'ticker': request.ticker,
            'analysis': analysis,
            'strategy': strategy,
            'risk_tolerance': request.risk_tolerance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/ai/workflow')
async def run_workflow(request: AnalysisRequest):
    """Run complete LangGraph workflow analysis"""
    if not os.getenv('GROQ_API_KEY'):
        raise HTTPException(status_code=400, detail='GROQ_API_KEY not set')
    
    try:
        workflow = get_ta_workflow()
        result = workflow.analyze(request.ticker)
        
        return {
            'ticker': request.ticker,
            'technical_analysis': result['technical_analysis'],
            'risk_assessment': result['risk_assessment'],
            'recommendation': result['final_recommendation'],
            'workflow_steps': result['messages']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/ai/agent/query')
async def agent_query(request: QueryRequest):
    """Query the autonomous AI agent"""
    if not os.getenv('GROQ_API_KEY'):
        raise HTTPException(status_code=400, detail='GROQ_API_KEY not set')
    
    try:
        agent = get_autonomous_agent()
        response = agent.analyze(request.query)
        
        return {
            'query': request.query,
            'response': response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/health')
async def health_check():
    return {
        'status': 'healthy',
        'ai_enabled': bool(os.getenv('GROQ_API_KEY')),
        'version': '2.0.0'
    }

if __name__ == '__main__':
    uvicorn.run('src.api.main:app', host='0.0.0.0', port=8000, reload=True)
