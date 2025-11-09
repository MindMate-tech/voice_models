#!/bin/bash
# Startup script for Cloud Run and other containerized deployments
# Ensures proper port configuration

# Get port from environment variable (Cloud Run sets this to 8080)
PORT=${PORT:-8080}

echo "🚀 Starting Voice Dementia Detection API"
echo "📍 Port: $PORT"
echo "🌐 Host: 0.0.0.0"
echo ""

# Start uvicorn with the configured port
exec uvicorn api:app --host 0.0.0.0 --port "$PORT" --log-level info

