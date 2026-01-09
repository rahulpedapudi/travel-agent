"""
CONFIGURATION
=============
Centralized settings with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Required
    google_api_key: str = Field(..., description="Gemini API key")
    
    # Optional
    google_maps_api_key: Optional[str] = Field(None, description="Google Maps API key")
    api_key: Optional[str] = Field(None, description="API key for client authentication")
    
    # Server
    environment: str = Field("development", description="development/staging/production")
    port: int = Field(8080, description="Server port")
    host: str = Field("0.0.0.0", description="Server host")
    
    # LLM Model
    llm_model: str = Field("gemini-2.5-flash", description="LLM model for all agents")
    
    # Demo Mode - bypasses LLM with mock data
    # demo_mode: bool = Field(False, description="Enable demo mode with mock data")
    demo_mode: bool = Field(True, description="Enable demo mode with mock data")
    
    # CORS
    allowed_origins: str = Field("*", description="Comma-separated allowed origins")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Module-level constants - safe to import at module level
# These use environment variables directly to avoid circular import issues
import os
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

