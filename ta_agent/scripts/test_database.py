"""
Comprehensive database test suite
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all dependencies are installed"""
    print("🧪 Test 1: Dependencies")
    print("-" * 40)
    
    try:
        import sqlalchemy
        print(f"  ✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError:
        print("  ❌ SQLAlchemy not found")
        return False
    
    try:
        import pydantic_settings
        print("  ✅ pydantic-settings installed")
    except ImportError:
        print("  ❌ pydantic-settings not found")
        print("     Run: pip install pydantic-settings")
        return False
    
    try:
        from src.core.config import settings
        print("  ✅ Configuration loaded")
        print(f"     Database: {settings.DATABASE_URL.split('://')[0]}")
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False
    
    return True


def test_database_connection():
    """Test database connection"""
    print("\n🧪 Test 2: Database Connection")
    print("-" * 40)
    
    try:
        from src.db.session import engine, SessionLocal
        
        # Test connection
        with engine.connect() as conn:
            print("  ✅ Database connection successful")
        
        # Test session
        db = SessionLocal()
        db.close()
        print("  ✅ Session creation successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        return False


def test_database_tables():
    """Test if tables are created"""
    print("\n🧪 Test 3: Database Tables")
    print("-" * 40)
    
    try:
        from src.db.session import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['users', 'query_history', 'portfolio', 
                          'watchlist', 'alerts']
        
        for table in required_tables:
            if table in tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Table check failed: {e}")
        return False


def test_crud_operations():
    """Test Create, Read, Update, Delete"""
    print("\n🧪 Test 4: CRUD Operations")
    print("-" * 40)
    
    try:
        from src.db.session import SessionLocal
        from src.models.user import User
        from src.utils.auth_utils import get_password_hash
        from datetime import datetime
        
        db = SessionLocal()
        
        # CREATE
        test_email = f"test_{int(datetime.now().timestamp())}@example.com"
        test_username = f"test_{int(datetime.now().timestamp())}"
        
        test_user = User(
            email=test_email,
            username=test_username,
            hashed_password=get_password_hash("test123"),
            full_name="Test User"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"  ✅ CREATE: User {test_user.id} created")
        
        # READ
        user = db.query(User).filter(User.id == test_user.id).first()
        if user:
            print(f"  ✅ READ: User {user.id} found")
        else:
            print("  ❌ READ: User not found")
            db.close()
            return False
        
        # UPDATE
        user.full_name = "Updated Test User"
        db.commit()
        db.refresh(user)
        if user.full_name == "Updated Test User":
            print(f"  ✅ UPDATE: User {user.id} updated")
        else:
            print("  ❌ UPDATE: Failed")
            db.close()
            return False
        
        # DELETE
        user_id = test_user.id
        db.delete(user)
        db.commit()
        deleted_user = db.query(User).filter(User.id == user_id).first()
        if deleted_user is None:
            print(f"  ✅ DELETE: User {user_id} deleted")
        else:
            print("  ❌ DELETE: Failed")
            db.close()
            return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_relationships():
    """Test foreign key relationships"""
    print("\n🧪 Test 5: Relationships")
    print("-" * 40)
    
    try:
        from src.db.session import SessionLocal
        from src.models.user import User
        from src.models.query_history import QueryHistory
        from src.utils.auth_utils import get_password_hash
        from datetime import datetime
        
        db = SessionLocal()
        
        # Create user
        test_email = f"rel_test_{int(datetime.now().timestamp())}@example.com"
        test_username = f"rel_test_{int(datetime.now().timestamp())}"
        
        user = User(
            email=test_email,
            username=test_username,
            hashed_password=get_password_hash("test123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"  ✅ User {user.id} created")
        
        # Create query linked to user
        query = QueryHistory(
            user_id=user.id,
            query_text="Test query",
            query_type="test",
            ticker="TEST",
            result={"test": "result"},
            status="completed"
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        print(f"  ✅ Query {query.id} linked to User {user.id}")
        
        # Test relationship
        user_queries = db.query(QueryHistory).filter(
            QueryHistory.user_id == user.id
        ).all()
        
        if len(user_queries) > 0:
            print(f"  ✅ Relationship: Found {len(user_queries)} queries for user")
        else:
            print("  ❌ Relationship: No queries found")
            db.close()
            return False
        
        # Cleanup
        db.delete(query)
        db.delete(user)
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        print(f"  ❌ Relationship test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run complete test suite"""
    print("=" * 60)
    print("🎯 DATABASE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_imports),
        ("Connection", test_database_connection),
        ("Tables", test_database_tables),
        ("CRUD Operations", test_crud_operations),
        ("Relationships", test_relationships)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"  ✅ Passed: {passed}/{len(tests)}")
    print(f"  ❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
