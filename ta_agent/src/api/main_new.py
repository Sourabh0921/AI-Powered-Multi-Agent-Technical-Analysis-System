"""
FastAPI main application - Entry point for the API server.

Run with:
    uvicorn src.api.main:app --reload
    
Or:
    python -m uvicorn src.api.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..core.config import settings
from ..core.logging import logger
from ..db import init_db
from .v1.router import api_router


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Technical Analysis API with Authentication",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise
    
    # Check AI configuration
    if settings.ENABLE_AI:
        if settings.GROQ_API_KEY or settings.OPENAI_API_KEY:
            logger.info(f"✅ AI enabled - Provider: {settings.DEFAULT_LLM_PROVIDER}")
        else:
            logger.warning("⚠️  AI enabled but no API keys configured")
    else:
        logger.info("AI features disabled")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down application")


# Include API v1 router
app.include_router(api_router, prefix=settings.API_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """API root - health check and info"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "healthy",
        "docs": "/docs",
        "api": settings.API_PREFIX,
        "features": {
            "ai": settings.ENABLE_AI,
            "websocket": settings.ENABLE_WEBSOCKET,
            "backtest": settings.ENABLE_BACKTEST,
            "alerts": settings.ENABLE_ALERTS,
            "portfolio": settings.ENABLE_PORTFOLIO
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "available" if settings.ENABLE_AI else "disabled",
        "cache": "connected" if settings.CACHE_ENABLED else "disabled"
    }


# Run application
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
