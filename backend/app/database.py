from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This creates a file named "diamond_mind.db" in your main backend folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./diamond_mind.db"

# Create the engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models
Base = declarative_base()

# Helper function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()