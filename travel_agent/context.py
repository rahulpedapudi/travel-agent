from contextvars import ContextVar

# Context variable to store the current session ID
# Defaults to "default" if not set (e.g. during testing)
session_context: ContextVar[str] = ContextVar("session_id", default="default")
