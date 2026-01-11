"""
Database Usage Examples - Practical demonstrations

This file shows real-world examples of how we use the database
in the TA-Agent project.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from src.db.session import get_db, init_db
from src.models.user import User
from src.models.query_history import QueryHistory
from src.models.portfolio import Portfolio
from src.models.watchlist import Watchlist
from src.models.alert import Alert
from src.utils.auth_utils import get_password_hash, verify_password
from src.core.logging import logger


# =============================================================================
# EXAMPLE 1: User Registration & Authentication
# =============================================================================

def example_user_registration(db: Session, email: str, username: str, password: str):
    """
    Example: Register a new user
    
    Use Case: When user signs up on the platform
    """
    print("\n📝 Example 1: User Registration")
    print("-" * 50)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"❌ User with email {email} already exists")
        return None
    
    # Create new user
    new_user = User(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        full_name=f"Test User {username}",
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ User created successfully!")
    print(f"   ID: {new_user.id}")
    print(f"   Email: {new_user.email}")
    print(f"   Username: {new_user.username}")
    print(f"   Created: {new_user.created_at}")
    
    return new_user


def example_user_login(db: Session, email: str, password: str):
    """
    Example: Authenticate user
    
    Use Case: When user tries to login
    """
    print("\n🔐 Example 2: User Login")
    print("-" * 50)
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        print("❌ User not found")
        return None
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        print("❌ Invalid password")
        return None
    
    print(f"✅ Login successful!")
    print(f"   Welcome, {user.full_name}!")
    
    return user


# =============================================================================
# EXAMPLE 2: Query History Tracking
# =============================================================================

def example_save_query(db: Session, user_id: int, query_text: str, 
                       ticker: str, result: dict):
    """
    Example: Save AI query and result
    
    Use Case: When user asks "Should I buy AAPL?"
    """
    print("\n💾 Example 3: Saving Query History")
    print("-" * 50)
    
    query_record = QueryHistory(
        user_id=user_id,
        query_text=query_text,
        query_type="analyze",
        ticker=ticker,
        result=result,
        status="completed",
        completed_at=datetime.utcnow()
    )
    
    db.add(query_record)
    db.commit()
    db.refresh(query_record)
    
    print(f"✅ Query saved!")
    print(f"   ID: {query_record.id}")
    print(f"   Query: {query_record.query_text}")
    print(f"   Ticker: {query_record.ticker}")
    print(f"   Result: {query_record.result}")
    
    return query_record


def example_get_user_history(db: Session, user_id: int, limit: int = 10):
    """
    Example: Retrieve user's query history
    
    Use Case: Display history on dashboard
    """
    print(f"\n📜 Example 4: User Query History (Last {limit})")
    print("-" * 50)
    
    queries = db.query(QueryHistory).filter(
        QueryHistory.user_id == user_id
    ).order_by(QueryHistory.created_at.desc()).limit(limit).all()
    
    if not queries:
        print("   No queries found")
        return []
    
    for i, query in enumerate(queries, 1):
        print(f"\n   {i}. {query.query_text}")
        print(f"      Ticker: {query.ticker}")
        print(f"      Status: {query.status}")
        print(f"      Date: {query.created_at}")
    
    return queries


def example_get_popular_stocks(db: Session, days: int = 7):
    """
    Example: Find most analyzed stocks
    
    Use Case: Show trending stocks on homepage
    """
    print(f"\n📊 Example 5: Most Analyzed Stocks (Last {days} days)")
    print("-" * 50)
    
    from sqlalchemy import func
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    popular_stocks = db.query(
        QueryHistory.ticker,
        func.count(QueryHistory.ticker).label('count')
    ).filter(
        QueryHistory.created_at >= cutoff_date,
        QueryHistory.ticker.isnot(None)
    ).group_by(
        QueryHistory.ticker
    ).order_by(
        func.count(QueryHistory.ticker).desc()
    ).limit(10).all()
    
    for i, (ticker, count) in enumerate(popular_stocks, 1):
        print(f"   {i}. {ticker}: {count} queries")
    
    return popular_stocks


# =============================================================================
# EXAMPLE 3: Portfolio Management
# =============================================================================

def example_add_portfolio_position(db: Session, user_id: int, ticker: str, 
                                   quantity: int, buy_price: float):
    """
    Example: Add stock to portfolio
    
    Use Case: User buys stock and wants to track it
    """
    print("\n💼 Example 6: Add Portfolio Position")
    print("-" * 50)
    
    position = Portfolio(
        user_id=user_id,
        ticker=ticker,
        company_name=f"{ticker} Inc.",  # Would fetch from API
        quantity=quantity,
        buy_price=buy_price,
        total_invested=quantity * buy_price,
        buy_date=datetime.utcnow().date(),
        buy_reason="AI Recommended"
    )
    
    db.add(position)
    db.commit()
    db.refresh(position)
    
    print(f"✅ Position added!")
    print(f"   Ticker: {position.ticker}")
    print(f"   Quantity: {position.quantity} shares")
    print(f"   Buy Price: ${position.buy_price:.2f}")
    print(f"   Total Invested: ${position.total_invested:.2f}")
    
    return position


def example_update_portfolio_prices(db: Session, user_id: int, 
                                    current_prices: dict):
    """
    Example: Update portfolio with current prices
    
    Use Case: Refresh portfolio values from market data
    """
    print("\n🔄 Example 7: Update Portfolio Prices")
    print("-" * 50)
    
    positions = db.query(Portfolio).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_closed == False
    ).all()
    
    for position in positions:
        if position.ticker in current_prices:
            position.current_price = current_prices[position.ticker]
            position.calculate_metrics()  # Calculate P&L
    
    db.commit()
    
    print(f"✅ Updated {len(positions)} positions")
    for position in positions:
        print(f"\n   {position.ticker}:")
        print(f"      Current: ${position.current_price:.2f}")
        print(f"      P&L: ${position.profit_loss:.2f} "
              f"({position.profit_loss_percent:.2f}%)")
    
    return positions


# =============================================================================
# EXAMPLE 4: Watchlist Management
# =============================================================================

def example_add_to_watchlist(db: Session, user_id: int, ticker: str, notes: str):
    """
    Example: Add stock to watchlist
    
    Use Case: User wants to monitor a stock
    """
    print("\n👁️ Example 8: Add to Watchlist")
    print("-" * 50)
    
    watchlist_item = Watchlist(
        user_id=user_id,
        ticker=ticker,
        company_name=f"{ticker} Inc.",
        notes=notes,
        price_target=None  # User can set later
    )
    
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    
    print(f"✅ Added to watchlist!")
    print(f"   Ticker: {watchlist_item.ticker}")
    print(f"   Notes: {watchlist_item.notes}")
    
    return watchlist_item


# =============================================================================
# EXAMPLE 5: Alert Management
# =============================================================================

def example_create_price_alert(db: Session, user_id: int, ticker: str, 
                               target_price: float):
    """
    Example: Create price alert
    
    Use Case: Notify user when TSLA > $250
    """
    print("\n🔔 Example 9: Create Price Alert")
    print("-" * 50)
    
    alert = Alert(
        user_id=user_id,
        ticker=ticker,
        alert_type="price_above",
        condition={"operator": ">", "value": target_price},
        name=f"{ticker} above ${target_price}",
        description=f"Alert when {ticker} price exceeds ${target_price}",
        is_active=True,
        notification_method="email"
    )
    
    db.add(alert)
    db.commit()
    db.refresh(alert)
    
    print(f"✅ Alert created!")
    print(f"   Ticker: {alert.ticker}")
    print(f"   Condition: Price > ${target_price}")
    print(f"   Notification: {alert.notification_method}")
    
    return alert


# =============================================================================
# EXAMPLE 6: Analytics & Insights
# =============================================================================

def example_user_analytics(db: Session, user_id: int):
    """
    Example: Get user analytics
    
    Use Case: Show user statistics on profile page
    """
    print("\n📈 Example 10: User Analytics")
    print("-" * 50)
    
    from sqlalchemy import func
    
    # Total queries
    total_queries = db.query(func.count(QueryHistory.id)).filter(
        QueryHistory.user_id == user_id
    ).scalar()
    
    # Queries this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    queries_this_week = db.query(func.count(QueryHistory.id)).filter(
        QueryHistory.user_id == user_id,
        QueryHistory.created_at >= week_ago
    ).scalar()
    
    # Favorite stock (most queried)
    favorite = db.query(
        QueryHistory.ticker,
        func.count(QueryHistory.ticker).label('count')
    ).filter(
        QueryHistory.user_id == user_id,
        QueryHistory.ticker.isnot(None)
    ).group_by(QueryHistory.ticker).order_by(
        func.count(QueryHistory.ticker).desc()
    ).first()
    
    # Portfolio value
    portfolio_value = db.query(func.sum(Portfolio.current_value)).filter(
        Portfolio.user_id == user_id,
        Portfolio.is_closed == False
    ).scalar() or 0
    
    print(f"   Total Queries: {total_queries}")
    print(f"   Queries This Week: {queries_this_week}")
    print(f"   Favorite Stock: {favorite[0] if favorite else 'None'}")
    print(f"   Portfolio Value: ${portfolio_value:.2f}")
    
    return {
        "total_queries": total_queries,
        "queries_this_week": queries_this_week,
        "favorite_stock": favorite[0] if favorite else None,
        "portfolio_value": portfolio_value
    }


# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================

def run_all_examples():
    """
    Run all database examples
    
    This demonstrates how the database is used in real scenarios
    """
    print("\n" + "="*70)
    print("🎯 TA-AGENT DATABASE USAGE EXAMPLES")
    print("="*70)
    
    # Initialize database
    print("\n🔧 Initializing database...")
    init_db()
    
    # Create a database session
    from src.db.session import SessionLocal
    db = SessionLocal()
    
    try:
        # 1. User Registration
        user = example_user_registration(
            db, 
            email="trader@example.com",
            username="trader123",
            password="securepassword"
        )
        
        if not user:
            # User exists, login instead
            user = example_user_login(db, "trader@example.com", "securepassword")
        
        if not user:
            print("❌ Could not create or login user")
            return
        
        # 2. Save some queries
        example_save_query(
            db, user.id,
            query_text="Should I buy AAPL?",
            ticker="AAPL",
            result={"signal": "BUY", "rsi": 45, "confidence": 0.85}
        )
        
        example_save_query(
            db, user.id,
            query_text="Analyze TSLA",
            ticker="TSLA",
            result={"signal": "HOLD", "rsi": 55, "confidence": 0.70}
        )
        
        # 3. Get query history
        example_get_user_history(db, user.id)
        
        # 4. Popular stocks
        example_get_popular_stocks(db, days=30)
        
        # 5. Add portfolio positions
        example_add_portfolio_position(db, user.id, "AAPL", 100, 150.50)
        example_add_portfolio_position(db, user.id, "TSLA", 50, 245.75)
        
        # 6. Update portfolio prices
        current_prices = {"AAPL": 155.25, "TSLA": 250.00}
        example_update_portfolio_prices(db, user.id, current_prices)
        
        # 7. Add to watchlist
        example_add_to_watchlist(
            db, user.id, "NVDA",
            notes="Wait for RSI below 30"
        )
        
        # 8. Create alert
        example_create_price_alert(db, user.id, "TSLA", 260.00)
        
        # 9. User analytics
        example_user_analytics(db, user.id)
        
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    run_all_examples()
