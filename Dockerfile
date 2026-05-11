# KUERA AI — Docker Image
# Build: docker build -t kuera-ai .
# Run:   docker run -p 7777:7777 -p 8000:8000 -p 18789:18789 kuera-ai

FROM python:3.11-slim

LABEL maintainer="panomr5973 <panomr5973@gmail.com>"
LABEL version="3.2.0"
LABEL description="KUERA AI — Local-first AI workstation for audit workflows"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY gateway_server.py .
COPY start_api.py .
COPY start_dashboard.py .
COPY audit_toolkit.py .
COPY template_audit_spi.py .
COPY template_audit_kinerja.py .
COPY template_master.py .
COPY pdf_extractor.py .
COPY file_processor.py .
COPY KUERA_MANIFEST.json .
COPY config/ ./config/
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY tools/ ./tools/
COPY docs/ ./docs/

# Create directories for runtime data
RUN mkdir -p data/uploads data/processed logs memory models/llm

# Expose ports
# 7777: Control Panel (Flask)
# 8000: Canonical API (FastAPI)
# 18789: WebSocket Gateway
EXPOSE 7777 8000 18789

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7777/api/health')" || exit 1

# Run the unified control panel by default
CMD ["python", "main.py"]
