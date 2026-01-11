# query_schemas.py - Pydantic schemas for queries
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class QueryCreate(BaseModel):
    query_text: str = Field(..., min_length=1, max_length=5000)
    query_type: str = Field(default="general")  # general, analyze, backtest
    ticker: Optional[str] = None


class QueryResponse(BaseModel):
    id: int
    user_id: int
    query_text: str
    query_type: str
    ticker: Optional[str]
    result: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class QueryListResponse(BaseModel):
    total: int
    queries: list[QueryResponse]
