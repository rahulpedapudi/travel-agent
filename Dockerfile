# ================================================
# TRAVEL AGENT - DOCKERFILE
# ================================================
# Build: docker build -t travel-agent .
# Run: docker run -p 8080:8080 --env-file .env travel-agent
# ================================================

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY travel_agent/ ./travel_agent/

# Environment variables (override at runtime)
ENV PORT=8080
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run the API
CMD ["python", "-m", "uvicorn", "travel_agent.api:app", "--host", "0.0.0.0", "--port", "8080"]
