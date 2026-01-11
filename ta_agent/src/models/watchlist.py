"""
Watchlist Model - Stocks user wants to monitor

Enables users to:
- Keep track of interesting stocks
- Add notes and price targets
- Quick access to favorite stocks
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class Watchlist(Base):
    """
    User's stock watchlist - stocks they want to monitor
    """
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Stock information
    ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    
    # User notes and targets
    notes = Column(Text, nullable=True)  # User's notes about the stock
    price_target = Column(Float, nullable=True)  # Target price to buy/sell
    
    # Current data (cached)
    current_price = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", backref="watchlist")

    def __repr__(self):
        return f"<Watchlist {self.ticker} for user {self.user_id}>"


class WatchlistTag(Base):
    """
    Tags for organizing watchlist (e.g., "Tech", "Growth", "Dividend")
    """
    __tablename__ = "watchlist_tags"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    watchlist_id = Column(Integer, ForeignKey("watchlist.id"), nullable=False)
    tag = Column(String(50), nullable=False)  # "Tech", "Growth", etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
