"""
Database session management and initialization.

Supports both SQLite (development) and PostgreSQL (production).
Switch between them by changing DATABASE_URL in .env or config.py
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings
from ..core.logging import logger

# Database engine configuration
def get_engine_config():
    """
    Get database engine configuration based on DATABASE_URL.
    
    Returns appropriate settings for SQLite, PostgreSQL, MySQL, etc.
    """
    config = {
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
    }
    
    # SQLite-specific configuration
    if "sqlite" in settings.DATABASE_URL.lower():
        config["connect_args"] = {"check_same_thread": False}
        logger.info("Using SQLite database (Development mode)")
    
    # PostgreSQL-specific configuration
    elif "postgresql" in settings.DATABASE_URL.lower():
        config["pool_size"] = settings.DATABASE_POOL_SIZE
        config["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        config["pool_timeout"] = settings.DATABASE_POOL_TIMEOUT
        config["pool_pre_ping"] = True  # Verify connections before using
        logger.info("Using PostgreSQL database (Production mode)")
    
    # MySQL-specific configuration
    elif "mysql" in settings.DATABASE_URL.lower():
        config["pool_size"] = settings.DATABASE_POOL_SIZE
        config["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        config["pool_recycle"] = 3600  # Recycle connections every hour
        logger.info("Using MySQL database")
    
    return config


# Create engine with appropriate configuration
engine = create_engine(settings.DATABASE_URL, **get_engine_config())

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    try:
        # Import all models here to ensure they're registered with Base
        from ..models.user import User
        from ..models.query_history import QueryHistory
        from ..models.portfolio import Portfolio
        from ..models.watchlist import Watchlist, WatchlistTag
        from ..models.alert import Alert, AlertHistory
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def reset_db():
    """Reset database - drop and recreate all tables (DANGER!)"""
    logger.warning("WARNING: Resetting database - all data will be lost!")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset complete")
