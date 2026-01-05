from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class SwingStatus(str, enum.Enum):
    """Status of swing upload and processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    """User model for authentication and ownership of swing data"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship: One user has many swings
    swings = relationship("Swing", back_populates="user", cascade="all, delete-orphan")


class Swing(Base):
    """Swing model for video metadata and user ownership"""
    __tablename__ = "swings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255))
    video_url = Column(String)  # Future: S3/Supabase Storage URL
    
    # DM-56: Status tracking for upload cleanup
    status = Column(Enum(SwingStatus), nullable=False, default=SwingStatus.PROCESSING, index=True, server_default='processing')
    error_message = Column(Text, nullable=True)
    
    # DM-57: User-friendly metadata
    title = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="swings")
    analysis = relationship("AnalysisResult", back_populates="swing", uselist=False, cascade="all, delete-orphan")


class AnalysisResult(Base):
    """Analysis result model for AI-generated pose and swing data"""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    swing_id = Column(Integer, ForeignKey("swings.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # AI Analysis Data (stored as JSONB in PostgreSQL, JSON in SQLite)
    skeletal_data = Column(JSON)  # Full pose landmarks array from MediaPipe
    total_frames = Column(Integer)
    frames_with_person = Column(Integer)
    fps = Column(Float)
    bat_trail = Column(JSON)  # Array of bat positions
    
    # AI Feedback (legacy fields - may be deprecated in future)
    phase = Column(String(50))  # Stance, Load, Contact, etc.
    score = Column(Integer)
    feedback = Column(JSON)  # AI feedback array
    drill = Column(String(255))
    drill_explanation = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    swing = relationship("Swing", back_populates="analysis")
