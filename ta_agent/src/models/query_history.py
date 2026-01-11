# query_history.py - Query History Model
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    query_type = Column(String, default="general")  # general, analyze, backtest
    ticker = Column(String, nullable=True)
    result = Column(JSON, nullable=True)  # Store AI response as JSON
    status = Column(String, default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", backref="queries")

    def __repr__(self):
        return f"<QueryHistory {self.id} - {self.query_type}>"
