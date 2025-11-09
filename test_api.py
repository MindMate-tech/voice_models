#!/usr/bin/env python3
"""
Simple test client for the Voice Dementia Detection API.

Usage:
    python test_api.py <audio_file>
    python test_api.py audio.mp3
"""

import sys
import requests
import json

def test_api(audio_file, api_url="http://localhost:8000"):
    """
    Test the API with an audio file.
    
    Parameters:
    -----------
    audio_file : str
        Path to audio file
    api_url : str
        API base URL
    """
    print("=" * 60)
    print("Testing Voice Dementia Detection API")
    print("=" * 60)
    print(f"API URL: {api_url}")
    print(f"Audio file: {audio_file}")
    print()
    
    # Check health
    try:
        health_response = requests.get(f"{api_url}/health")
        health_data = health_response.json()
        print(f"✅ API Health: {health_data['status']}")
        print(f"   Model loaded: {health_data['model_loaded']}")
        print(f"   Device: {health_data['device']}")
        print()
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"   Make sure the API is running: uvicorn api:app --host 0.0.0.0 --port 8000")
        return
    
    # Upload and analyze file
    try:
        print("📤 Uploading file...")
        with open(audio_file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{api_url}/predict", files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis complete!")
            print()
            print("=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"Result: {result['result'].upper()}")
            print(f"Confidence: {result['confidence']*100:.2f}%")
            print()
            print("Probabilities:")
            print(f"  Normal:    {result['probabilities']['normal_percentage']:.2f}%")
            print(f"  Dementia: {result['probabilities']['dementia_percentage']:.2f}%")
            print()
            print(f"Message: {result['message']}")
            print()
            print(f"Audio Info:")
            print(f"  Length: {result['audio_info']['length_seconds']:.2f} seconds")
            print(f"  MFCC Shape: {result['audio_info']['mfcc_features_shape']}")
            print()
            print(f"Note: {result['note']}")
            print("=" * 60)
            
            # Pretty print full JSON
            print("\nFull JSON Response:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    
    except FileNotFoundError:
        print(f"❌ Error: File not found: {audio_file}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <audio_file> [api_url]")
        print("Example: python test_api.py audio.mp3")
        print("Example: python test_api.py audio.mp3 http://localhost:8000")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    test_api(audio_file, api_url)

