"""
Authentication middleware for DiamondMind backend.
Provides dependency injection for protected endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.supabase_client import verify_token
from app.database import get_db
from app.models import User

logger = logging.getLogger("backend.auth")

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Verifies the Supabase JWT token and returns the corresponding User from database.
    Creates user in local DB if they don't exist yet (first login after Supabase signup).
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        User object from database
        
    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    token = credentials.credentials
    
    logger.info(f"🔑 Attempting to verify token for /api/profile")
    
    # Verify token with Supabase
    try:
        supabase_user = verify_token(token)
    except Exception as e:
        logger.error(f"❌ Token verification exception: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not supabase_user:
        logger.warning("⚠️ Authentication failed: invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    supabase_id = supabase_user["id"]
    email = supabase_user["email"]
    
    # Look up user in local database by supabase_id
    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    
    if not user:
        # User exists in Supabase but not in local DB - create them
        logger.info(f"🆕 Creating new user in local DB: {email}")
        
        # Generate username from email (before @ symbol)
        username = email.split("@")[0]
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User(
            supabase_id=supabase_id,
            email=email,
            username=username
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"✅ User created: {user.username} (ID: {user.id})")
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, or None if not.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Bearer token
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        supabase_user = verify_token(token)
        
        if not supabase_user:
            return None
        
        user = db.query(User).filter(User.supabase_id == supabase_user["id"]).first()
        return user
        
    except Exception as e:
        logger.warning(f"⚠️ Optional auth failed: {str(e)}")
        return None
