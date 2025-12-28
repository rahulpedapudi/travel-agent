"""
FIREBASE AUTHENTICATION
========================
Firebase Admin SDK setup and auth dependency for FastAPI.
"""

import os
from typing import Optional
from fastapi import HTTPException, Header

import firebase_admin
from firebase_admin import credentials, auth

import logging
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
# Uses FIREBASE_SERVICE_ACCOUNT_KEY env var for the path to service account JSON
_firebase_initialized = False

def init_firebase():
    """Initialize Firebase Admin SDK (called once at startup)."""
    global _firebase_initialized
    if _firebase_initialized:
        return
    
    # Load .env file (handles both root and travel_agent/.env)
    from dotenv import load_dotenv
    load_dotenv()  # Load from current directory
    load_dotenv("travel_agent/.env")  # Also try subdirectory
    
    # Check for service account key file
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    
    if service_account_path:
        logger.info(f"Firebase: Looking for service account at: {service_account_path}")
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase: Initialized with service account key")
        else:
            raise FileNotFoundError(f"Firebase service account key not found at: {service_account_path}")
    else:
        # Use default credentials (GOOGLE_APPLICATION_CREDENTIALS env var)
        # This works in Cloud Run, GCE, etc.
        logger.info("Firebase: Using default credentials (GOOGLE_APPLICATION_CREDENTIALS)")
        firebase_admin.initialize_app()
    
    _firebase_initialized = True


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Verify Firebase ID token from Authorization header.
    Returns decoded token with user info (uid, email, etc.)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    token = authorization.split("Bearer ")[1]
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # Contains: uid, email, name, etc.
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Token revoked")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_optional_user(authorization: Optional[str] = Header(None)):
    """
    Same as get_current_user but returns None instead of raising error.
    Useful for endpoints that work with or without auth.
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
