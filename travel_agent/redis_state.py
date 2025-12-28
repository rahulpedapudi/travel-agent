"""
REDIS STATE SERVICE
====================
Production-ready state storage using Redis.

Falls back to in-memory if Redis is not available.
"""

import json
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

# Try to import redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed, using in-memory storage")


class RedisStateService:
    """Redis-backed state storage with automatic fallback."""
    
    def __init__(self):
        self.redis_client = None
        self.fallback_store = {}  # In-memory fallback
        self.ttl = 86400 * 7  # 7 days TTL for sessions
        
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                try:
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    self.redis_client.ping()
                    logger.info("Redis: Connected successfully")
                except Exception as e:
                    logger.warning(f"Redis: Connection failed ({e}), using fallback")
                    self.redis_client = None
            else:
                logger.info("Redis: REDIS_URL not set, using in-memory fallback")
    
    def _key(self, session_id: str) -> str:
        """Generate Redis key for session state."""
        return f"travel_agent:state:{session_id}"
    
    def _owner_key(self, session_id: str) -> str:
        """Generate Redis key for session ownership."""
        return f"travel_agent:owner:{session_id}"
    
    def get_state(self, session_id: str) -> dict:
        """Get state for a session."""
        if self.redis_client:
            try:
                data = self.redis_client.get(self._key(session_id))
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback or create new
        if session_id not in self.fallback_store:
            self.fallback_store[session_id] = self._empty_state()
        return self.fallback_store[session_id]
    
    def set_state(self, session_id: str, state: dict) -> None:
        """Save state for a session."""
        if self.redis_client:
            try:
                self.redis_client.setex(
                    self._key(session_id),
                    self.ttl,
                    json.dumps(state)
                )
                return
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fallback
        self.fallback_store[session_id] = state
    
    def set_owner(self, session_id: str, user_id: str) -> None:
        """Record session ownership."""
        if self.redis_client:
            try:
                self.redis_client.setex(self._owner_key(session_id), self.ttl, user_id)
                return
            except Exception as e:
                logger.error(f"Redis set owner error: {e}")
        
        # Fallback - store in state
        self.fallback_store[f"owner:{session_id}"] = user_id
    
    def get_owner(self, session_id: str) -> Optional[str]:
        """Get session owner."""
        if self.redis_client:
            try:
                return self.redis_client.get(self._owner_key(session_id))
            except Exception as e:
                logger.error(f"Redis get owner error: {e}")
        
        return self.fallback_store.get(f"owner:{session_id}")
    
    def delete_state(self, session_id: str) -> None:
        """Delete session state."""
        if self.redis_client:
            try:
                self.redis_client.delete(self._key(session_id))
                self.redis_client.delete(self._owner_key(session_id))
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        self.fallback_store.pop(session_id, None)
        self.fallback_store.pop(f"owner:{session_id}", None)
    
    def _empty_state(self) -> dict:
        """Create empty state structure."""
        return {
            "preferences": {},
            "hotels": [],
            "restaurants": [],
            "attractions": [],
            "recommended_activities": [],
            "itinerary": [],
            "phase": "clarifying",
            "warnings": []
        }


# Global instance
state_service = RedisStateService()
