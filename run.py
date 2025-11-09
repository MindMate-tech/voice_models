#!/usr/bin/env python3
"""
Startup script for Render deployment.
This ensures proper Python path setup before starting the server.
"""
import os
import sys

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add current directory to Python path if not already there
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now import and run uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

