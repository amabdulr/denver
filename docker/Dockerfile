# ============================================================
# Denver App – Cisco Documentation Assistant
# Multi-stage Docker build
# ============================================================

# ---------- Stage 1: builder ----------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build-time OS deps (needed by some pip packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install minimal runtime OS deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy the application source code
COPY . .

# Create directories the app may need at runtime
RUN mkdir -p /app/data /app/scour_output /root/.denver_vectorstore

# Streamlit config – headless mode, CORS disabled for container use
RUN mkdir -p /root/.streamlit && \
    cat > /root/.streamlit/config.toml <<'EOF'
[server]
headless = true
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
base = "dark"
EOF

# Expose Streamlit default port
EXPOSE 8501

# Health check – Streamlit responds on /_stcore/health
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default entrypoint: run via start.py (pre-loads vector store, then launches Streamlit)
ENTRYPOINT ["python", "start.py"]
