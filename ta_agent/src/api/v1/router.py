"""
API v1 main router - aggregates all endpoint routers.
"""
from fastapi import APIRouter
from .endpoints import auth, analysis, ai, sentiment, comprehensive
from ..queries import router as queries_router
from ..rag_routes import router as rag_router

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(sentiment.router, tags=["sentiment"])
api_router.include_router(comprehensive.router, tags=["comprehensive-analysis"])
api_router.include_router(queries_router, prefix="/queries", tags=["queries"])
api_router.include_router(rag_router, prefix="/rag", tags=["rag"])
