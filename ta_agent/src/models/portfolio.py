"""
Portfolio Model - Track user's stock positions

This table stores all stock positions owned by users, enabling:
- Portfolio management
- P&L tracking
- Performance analysis
- Buy/Sell history
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class Portfolio(Base):
    """
    User's stock portfolio - tracks all positions
    """
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Stock information
    ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    
    # Position details
    quantity = Column(Integer, nullable=False)  # Number of shares
    buy_price = Column(Float, nullable=False)  # Average purchase price
    current_price = Column(Float, nullable=True)  # Latest market price
    
    # Financial metrics
    total_invested = Column(Float, nullable=False)  # quantity * buy_price
    current_value = Column(Float, nullable=True)  # quantity * current_price
    profit_loss = Column(Float, nullable=True)  # current_value - total_invested
    profit_loss_percent = Column(Float, nullable=True)  # (P&L / invested) * 100
    
    # Position metadata
    buy_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False)  # True if position sold
    sell_price = Column(Float, nullable=True)
    sell_date = Column(Date, nullable=True)
    
    # Notes and tracking
    notes = Column(String(500), nullable=True)
    buy_reason = Column(String(200), nullable=True)  # "AI recommended", "Manual"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="portfolio")

    def __repr__(self):
        return f"<Portfolio {self.ticker}: {self.quantity} shares @ ${self.buy_price}>"
    
    def calculate_metrics(self):
        """Calculate current P&L metrics"""
        if self.current_price:
            self.current_value = self.quantity * self.current_price
            self.profit_loss = self.current_value - self.total_invested
            self.profit_loss_percent = (self.profit_loss / self.total_invested) * 100
