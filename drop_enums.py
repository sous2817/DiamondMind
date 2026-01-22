import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv("backend/.env")
db_url = os.environ.get("DATABASE_URL")

print(f"Connecting to: {db_url}")

engine = create_engine(db_url)
with engine.connect() as conn:
    print("✅ Connected!")
    
    # Drop old ENUM types
    try:
        print("🗑️  Dropping old ENUM types...")
        conn.execute(text("DROP TYPE IF EXISTS swingstatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS agegroup CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS handedness CASCADE"))
        conn.commit()
        print("✅ ENUM types dropped successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
