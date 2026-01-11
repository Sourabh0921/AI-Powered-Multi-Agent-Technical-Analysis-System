"""
Script to initialize the database with tables.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db.session import init_db
from src.core.logging import logger


def main():
    """Initialize the database"""
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized successfully!")
        print("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
