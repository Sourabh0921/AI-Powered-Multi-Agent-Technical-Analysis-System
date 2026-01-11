# db.py
import sqlite3
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_PATH = Path(__file__).resolve().parents[2] / 'data' / 'ta_agent.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from ..models.user import User
    from ..models.query_history import QueryHistory
    Base.metadata.create_all(bind=engine)


# Legacy functions for backward compatibility
def to_sql(df: pd.DataFrame, table: str):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table, conn, if_exists='replace')
    conn.close()


def read_sql(table: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f'SELECT * FROM "{table}"', conn, parse_dates=['index'])
    conn.close()
    return df
