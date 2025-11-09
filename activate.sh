#!/bin/bash
# Activation script for voice_model virtual environment
# Usage: source activate.sh

cd "$(dirname "$0")"
source venv/bin/activate
echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"

