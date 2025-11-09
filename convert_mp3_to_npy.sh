#!/bin/bash
# Simple wrapper script to automatically convert WAV files to .npy files
# Updated for nested structure: data/[Person Name]/[PersonName]_[number].wav
# Usage: ./convert_mp3_to_npy.sh [input_directory]

cd "$(dirname "$0")"
source venv/bin/activate

INPUT_DIR="${1:-data}"

if [ ! -d "$INPUT_DIR" ]; then
    echo "Creating directory: $INPUT_DIR"
    mkdir -p "$INPUT_DIR"
    echo ""
    echo "📁 Please organize your WAV files in: $INPUT_DIR/[Person Name]/[PersonName]_[number].wav"
    echo "   Example: data/John Doe/JohnDoe_0.wav"
    echo "   Then run this script again to convert them automatically."
    exit 0
fi

echo "🔄 Automatically converting audio files in: $INPUT_DIR"
echo "   Structure: $INPUT_DIR/[Person Name]/[PersonName]_[number].wav"
echo ""

python auto_convert_audio.py "$INPUT_DIR"

