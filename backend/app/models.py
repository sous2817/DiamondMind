from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from .database import Base

class SwingAnalysis(Base):
    __tablename__ = "swings"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    
    # Store the AI's results
    phase = Column(String) # Stance, Load, Contact, etc.
    score = Column(Integer)
    feedback = Column(JSON) # We can store the list of strings as JSON
    drill = Column(String)
    drill_explanation = Column(String)
    
    # Keep track of when it happened
    created_at = Column(DateTime, default=datetime.utcnow)