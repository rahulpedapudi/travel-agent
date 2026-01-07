"""
STRUCTURED LOGGING
==================
Lightweight structured logging using structlog.

Tracks:
- Request start/end times
- Token usage
- Tool calls
- Exceptions
"""

import structlog
import logging
import time
from typing import Optional, Any
from datetime import datetime
from functools import wraps
import json
import os


# Configure structlog
def configure_logging():
    """Configure structlog for production use."""
    
    # Determine if we're in production
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    # Shared processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if is_production:
        # JSON output for production (Cloud Run logs)
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Pretty console output for development
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.format_exc_info,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


# Initialize on import
configure_logging()


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name or __name__)


class RequestLogger:
    """Context manager for logging request lifecycle."""
    
    def __init__(
        self,
        session_id: str,
        user_id: str = None,
        endpoint: str = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.endpoint = endpoint
        self.start_time = None
        self.tool_calls = []
        self.token_usage = {"input": 0, "output": 0, "total": 0}
        self.log = get_logger("request")
    
    def __enter__(self):
        self.start_time = time.time()
        self.log.info(
            "request_started",
            session_id=self.session_id,
            user_id=self.user_id,
            endpoint=self.endpoint,
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.log.error(
                "request_failed",
                session_id=self.session_id,
                duration_ms=round(duration_ms, 2),
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                tool_calls=self.tool_calls,
                token_usage=self.token_usage,
            )
        else:
            self.log.info(
                "request_completed",
                session_id=self.session_id,
                duration_ms=round(duration_ms, 2),
                tool_calls=self.tool_calls,
                tool_count=len(self.tool_calls),
                token_usage=self.token_usage,
            )
        
        return False  # Don't suppress exceptions
    
    def log_tool_call(self, tool_name: str, duration_ms: float = None, success: bool = True):
        """Log a tool call."""
        call_info = {
            "name": tool_name,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if duration_ms is not None:
            call_info["duration_ms"] = round(duration_ms, 2)
        
        self.tool_calls.append(call_info)
        self.log.debug("tool_called", **call_info)
    
    def log_token_usage(self, input_tokens: int = 0, output_tokens: int = 0):
        """Log token usage."""
        self.token_usage["input"] += input_tokens
        self.token_usage["output"] += output_tokens
        self.token_usage["total"] = self.token_usage["input"] + self.token_usage["output"]
    
    def log_agent_call(self, agent_name: str, status: str = "started"):
        """Log when a sub-agent is called."""
        self.log.info(
            "agent_call",
            session_id=self.session_id,
            agent=agent_name,
            status=status,
        )


def log_function(logger_name: str = None):
    """Decorator to log function calls with timing."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            log = get_logger(logger_name or func.__module__)
            start = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                log.debug(
                    "function_completed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                log.error(
                    "function_failed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            log = get_logger(logger_name or func.__module__)
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                log.debug(
                    "function_completed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                log.error(
                    "function_failed",
                    function=func.__name__,
                    duration_ms=round(duration_ms, 2),
                    error=str(e),
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Export commonly used items
__all__ = [
    "get_logger",
    "RequestLogger",
    "log_function",
    "configure_logging",
]
