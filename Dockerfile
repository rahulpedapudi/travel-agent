# ================================================
# TRAVEL AGENT - PRODUCTION DOCKERFILE
# ================================================
# Build: docker build -t travel-agent .
# Run: docker run -p 8080:8080 --env-file .env travel-agent
# ================================================

# Stage 1: Build dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python packages to user directory
RUN pip install --no-cache-dir --user -r requirements.txt


# Stage 2: Production image
FROM python:3.12-slim

WORKDIR /app

# Create non-root user FIRST (before copying files)
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages to appuser's directory (not root's)
COPY --from=builder /root/.local /home/appuser/.local
RUN chown -R appuser:appuser /home/appuser/.local

# Copy application code with correct ownership
COPY --chown=appuser:appuser travel_agent/ ./travel_agent/

# Switch to non-root user
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

# Environment variables (override at runtime)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the API with uvicorn (production workers)
CMD ["python", "-m", "uvicorn", "travel_agent.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
