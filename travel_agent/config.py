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
    
    # CORS
    allowed_origins: str = Field("*", description="Comma-separated allowed origins")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
