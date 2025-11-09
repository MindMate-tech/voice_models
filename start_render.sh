#!/bin/bash
# Startup script for Render deployment
# This ensures the Python path is set correctly

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Add current directory to PYTHONPATH if not already there
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"

# Start uvicorn
exec python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}

