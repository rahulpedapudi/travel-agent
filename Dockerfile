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

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY travel_agent/ ./travel_agent/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

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
CMD ["uvicorn", "travel_agent.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
