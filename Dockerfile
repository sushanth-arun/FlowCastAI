# =============================================================
# FlowCast AI - Multi-Architecture Dockerfile (IBM Z / s390x & x86_64)
# Compatible with IBM LinuxONE, z/OS Container Extensions (zCX), & Cloud
# =============================================================

FROM python:3.11-slim

# Avoid prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Upgrade pip and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy serialized model artifacts, datasets, and source code
COPY artifacts/ ./artifacts/
COPY data/ ./data/
COPY src/ ./src/
COPY README.md .

# Expose port for FastAPI Orchestrator Gateway & Web Dashboard
EXPOSE 8000

# Health check to ensure service readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Launch FlowCast AI Gateway
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
