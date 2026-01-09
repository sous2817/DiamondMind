"""
Supabase client configuration for DiamondMind backend.
Provides authentication token verification and user management.
"""
import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger("backend.supabase")

# Supabase credentials from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://zgwxrfetbplatwpimmec.supabase.co")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Initialize Supabase client with service role key (backend only)
supabase: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client singleton"""
    global supabase
    
    if supabase is None:
        if not SUPABASE_SERVICE_KEY:
            logger.error("❌ SUPABASE_SERVICE_KEY not set in environment")
            raise ValueError("Supabase service key not configured")
        
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info(f"✅ Supabase client initialized: {SUPABASE_URL}")
    
    return supabase


def verify_token(access_token: str) -> Optional[dict]:
    """
    Verify a Supabase JWT access token and return user data.
    
    Args:
        access_token: JWT token from Authorization header
        
    Returns:
        User data dict with 'id', 'email', etc. or None if invalid
    """
    try:
        client = get_supabase_client()
        
        # Verify token by getting user with it
        response = client.auth.get_user(access_token)
        
        if response and response.user:
            logger.info(f"✅ Token verified for user: {response.user.email}")
            return {
                "id": response.user.id,
                "email": response.user.email,
                "email_confirmed": response.user.email_confirmed_at is not None,
                "created_at": response.user.created_at
            }
        
        logger.warning("⚠️ Invalid token: no user found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Token verification failed: {str(e)}")
        return None
