# Multi-stage build for smaller image
FROM python:3.11-alpine3.18

# Install minimal runtime dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app-minimal.py ./app.py
COPY nsjail.cfg .

# Create non-root user
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /tmp && chmod 1777 /tmp

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run as non-root user
USER appuser

# Start the application
CMD ["python3", "app.py"]
