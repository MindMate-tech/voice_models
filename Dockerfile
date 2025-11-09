# Dockerfile for Voice Dementia Detection API
# Can be used with Docker, Railway, Fly.io, AWS, GCP, Azure, etc.

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start_server.sh

# Expose port (Cloud Run uses 8080, but this is informational)
# The actual port is determined by the PORT environment variable
EXPOSE 8080

# Health check - uses PORT environment variable (Cloud Run sets this to 8080)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os, requests; port = os.environ.get('PORT', '8080'); requests.get(f'http://localhost:{port}/health', timeout=5)" || exit 1

# Run the application using startup script
# The script handles PORT environment variable (Cloud Run sets this to 8080)
CMD ["./start_server.sh"]

