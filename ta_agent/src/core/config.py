"""
Centralized configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "TA-Agent"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # API Configuration
    API_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8501"]
    
    # Security
    SECRET_KEY: str = "your-secret-jwt-key-change-this-in-production-make-it-long-and-random"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/databases/ta_agent.db"
    # Examples for different databases:
    # SQLite: sqlite:///./data/databases/ta_agent.db
    # PostgreSQL: postgresql://ta_user:ta_password@localhost:5432/ta_agent
    # PostgreSQL (Async): postgresql+asyncpg://ta_user:ta_password@localhost:5432/ta_agent
    # MySQL: mysql+pymysql://user:password@localhost:3306/ta_agent
    
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    
    # LLM/AI Configuration
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "groq"  # openai, groq, google, anthropic
    DEFAULT_LLM_MODEL: str = "openai/gpt-oss-120b"
    LLM_MODEL: str = "openai/gpt-oss-120b"  # Alias for DEFAULT_LLM_MODEL
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2000
    
    # Sentiment Analysis API Keys
    NEWSAPI_KEY: Optional[str] = None  # https://newsapi.org/
    ALPHA_VANTAGE_KEY: Optional[str] = None  # https://www.alphavantage.co/
    FINNHUB_KEY: Optional[str] = None  # https://finnhub.io/
    TWITTER_BEARER_TOKEN: Optional[str] = None  # https://developer.twitter.com/
    REDDIT_CLIENT_ID: Optional[str] = None  # https://www.reddit.com/prefs/apps
    REDDIT_CLIENT_SECRET: Optional[str] = None
    STOCKTWITS_TOKEN: Optional[str] = None  # https://stocktwits.com/developers
    
    # Sentiment Analysis Configuration
    SENTIMENT_ENABLED: bool = True
    SENTIMENT_CACHE_TTL: int = 600  # 10 minutes
    SENTIMENT_NEWS_WEIGHT: float = 0.35
    SENTIMENT_SOCIAL_WEIGHT: float = 0.30
    SENTIMENT_SEC_WEIGHT: float = 0.20
    SENTIMENT_EARNINGS_WEIGHT: float = 0.15
    
    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = 8501
    
    # Redis (Caching)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_ENABLED: bool = False
    CACHE_TTL: int = 300  # 5 minutes
    
    # Feature Flags
    ENABLE_WEBSOCKET: bool = True
    ENABLE_AI: bool = True
    ENABLE_BACKTEST: bool = True
    ENABLE_ALERTS: bool = True
    ENABLE_PORTFOLIO: bool = True
    
    # Data Configuration
    DATA_FETCH_TIMEOUT: int = 30
    DEFAULT_PERIOD: str = "1y"
    DEFAULT_INTERVAL: str = "1d"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_DIR: Path = DATA_DIR / "databases"
    CACHE_DIR: Path = DATA_DIR / "cache"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
