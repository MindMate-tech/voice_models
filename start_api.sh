#!/bin/bash
# Script to start the FastAPI server with proper environment setup

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment not found!"
    echo "   Please create it first: python3 -m venv venv"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import torch" 2>/dev/null || {
    echo "❌ Error: torch not found in virtual environment"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
}

python3 -c "import fastapi" 2>/dev/null || {
    echo "❌ Error: fastapi not found in virtual environment"
    echo "   Installing FastAPI..."
    pip install fastapi uvicorn[standard] python-multipart
}

# Start the API server
echo ""
echo "Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "Interactive docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn api:app --host 0.0.0.0 --port 8000 --reload

