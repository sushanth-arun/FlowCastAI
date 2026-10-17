# =============================================================
# FlowCast AI - Multi-Architecture Dockerfile (IBM Z / s390x & x86_64)
# Compatible with IBM LinuxONE, z/OS Container Extensions (zCX), & Cloud
# Uses Ubuntu 24.04 with pre-compiled native s390x system packages (Zero C/Fortran compile)
# =============================================================

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install pre-compiled native s390x ML & runtime packages directly from distribution
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-numpy \
    python3-scipy \
    python3-pandas \
    python3-sklearn \
    python3-joblib \
    python3-fastapi \
    python3-uvicorn \
    python3-pydantic \
    python3-requests \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pure-Python glue dependency without compilation
RUN pip3 install --break-system-packages --no-cache-dir --no-deps sklearn-pandas

# Set working directory
WORKDIR /app

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

# Launch FlowCast AI Gateway using native Python
CMD ["python3", "-m", "uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
