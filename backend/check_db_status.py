"""
Quick script to check swing status in the local SQLite database.
Run this from the backend directory: python check_db_status.py
"""
import os
import sys

# CRITICAL: Force SQLite by unsetting DATABASE_URL BEFORE any app imports
# This must happen before database.py is imported
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

# Also check if it's in a .env file and warn the user
from pathlib import Path
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print("⚠️  Note: .env file detected. This script uses local SQLite, not production database.\n")

# Now safe to import app modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models
sys.path.insert(0, str(Path(__file__).parent))
from app.models import Base, Swing, SwingStatus

# Create SQLite engine directly
SQLALCHEMY_DATABASE_URL = "sqlite:///./diamond_mind.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    db = SessionLocal()
    try:
        swings = db.query(Swing).all()
        
        print(f"\n{'='*60}")
        print(f"SWING DATABASE STATUS (Local SQLite)")
        print(f"{'='*60}\n")
        print(f"Total swings: {len(swings)}\n")
        
        if len(swings) == 0:
            print("No swings found in database.")
            print("The database may be empty or tables may not exist yet.")
            print("Start the backend server to create tables automatically.\n")
            return
        
        # Group by status
        status_counts = {}
        for swing in swings:
            status = swing.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("Status Summary:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        print(f"\n{'='*60}")
        print("Swing Details:")
        print(f"{'='*60}\n")
        
        for swing in swings:
            print(f"Swing ID: {swing.id}")
            print(f"  Status: {swing.status.value}")
            print(f"  Filename: {swing.filename}")
            print(f"  Title: {swing.title or '(none)'}")
            print(f"  User ID: {swing.user_id}")
            print(f"  Created: {swing.created_at}")
            if swing.error_message:
                print(f"  Error: {swing.error_message[:100]}...")
            print()
        
    except Exception as e:
        print(f"❌ Error reading database: {str(e)}")
        print("\nThe database may not exist yet or tables haven't been created.")
        print("Start the backend server to initialize the database.\n")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
