"""
Alerts Model - Price and pattern alerts for stocks

Enables automated monitoring and notifications when:
- Price reaches target
- RSI enters certain range
- MACD crosses
- Pattern detected
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..db.session import Base


class Alert(Base):
    """
    User-defined alerts for stock monitoring
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Stock information
    ticker = Column(String(10), nullable=False, index=True)
    
    # Alert configuration
    alert_type = Column(String(50), nullable=False)  # price_above, price_below, rsi_oversold, etc.
    condition = Column(JSON, nullable=False)  # {"operator": ">", "value": 150}
    
    # Alert details
    name = Column(String(100), nullable=True)  # User-friendly name
    description = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    triggered_value = Column(Float, nullable=True)  # Value when triggered
    
    # Notification settings
    notification_method = Column(String(20), default="email")  # email, sms, push
    notification_sent = Column(Boolean, default=False)
    
    # Frequency settings
    repeat = Column(Boolean, default=False)  # Re-trigger if condition met again
    cooldown_minutes = Column(Integer, default=60)  # Wait before re-triggering
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_checked = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship("User", backref="alerts")

    def __repr__(self):
        return f"<Alert {self.name or self.alert_type} for {self.ticker}>"


class AlertHistory(Base):
    """
    History of triggered alerts - keeps audit trail
    """
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trigger details
    triggered_value = Column(Float, nullable=False)
    condition_met = Column(JSON, nullable=False)
    market_data = Column(JSON, nullable=True)  # Snapshot of market data
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_error = Column(String(500), nullable=True)
    
    # Timestamp
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AlertHistory {self.alert_id} triggered at {self.triggered_at}>"
