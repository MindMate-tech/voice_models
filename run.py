#!/usr/bin/env python3
"""
Bulletproof startup script for Render deployment.
Handles all common deployment issues and provides detailed diagnostics.
"""
import os
import sys
import traceback

def setup_environment():
    """Set up Python environment for deployment."""
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script's directory (CRITICAL for Render)
    os.chdir(current_dir)
    
    # CRITICAL: Remove any parent 'src' directory from Python path
    # Render deploys to /opt/render/project/src/voice_model/
    # We want to keep /opt/render/project/src/voice_model/ but remove /opt/render/project/src/
    # This prevents Python from trying to import 'src' as a module
    filtered_path = []
    for p in sys.path:
        # Keep the current directory (voice_model) even if it contains 'src' in the path
        if p == current_dir:
            filtered_path.append(p)
        # Keep paths that don't contain 'src'
        elif 'src' not in p:
            filtered_path.append(p)
        # Remove paths that end with 'src' or have 'src' as a parent directory
        # (these would cause Python to try to import 'src' as a module)
        elif not p.endswith('src') and not p.endswith('src/'):
            # Only keep if it's a subdirectory of our current_dir
            if current_dir in p or p in current_dir:
                filtered_path.append(p)
    sys.path = filtered_path
    
    # Add current directory to Python path (MUST be first and ONLY the voice_model dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Add azrt2021 subdirectory to path
    azrt2021_dir = os.path.join(current_dir, 'azrt2021')
    if azrt2021_dir not in sys.path and os.path.exists(azrt2021_dir):
        sys.path.insert(0, azrt2021_dir)
    
    # IMPORTANT: Do NOT add parent directory - it contains 'src' which causes import errors
    # The rootDir setting in render.yaml should handle the working directory
    
    return current_dir

def verify_files(current_dir):
    """Verify all required files exist."""
    required_files = ['api.py', 'requirements.txt']
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ERROR: Missing required files: {', '.join(missing_files)}")
        print(f"Current directory: {current_dir}")
        print(f"Files present: {os.listdir(current_dir)}")
        return False
    
    return True

def print_diagnostics(current_dir):
    """Print diagnostic information for troubleshooting."""
    print("=" * 70)
    print("DEPLOYMENT DIAGNOSTICS")
    print("=" * 70)
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {current_dir}")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Python path (filtered to remove 'src' references):")
    for i, path in enumerate(sys.path[:10], 1):
        # Highlight if path contains 'src' (which we want to avoid)
        marker = " ⚠️  (contains 'src')" if 'src' in path and path != current_dir else ""
        print(f"  {i}. {path}{marker}")
    print()
    
    # Check if we're in the right place (should be in voice_model, not src)
    if 'src' in current_dir and current_dir.endswith('voice_model'):
        print("✅ Correctly in voice_model directory (even though path contains 'src')")
    elif 'src' not in current_dir:
        print("✅ Path doesn't contain 'src' - good!")
    else:
        print("⚠️  Warning: Path structure might be incorrect")
    print()
    
    # Check if api.py exists and is readable
    api_path = os.path.join(current_dir, "api.py")
    if os.path.exists(api_path):
        print(f"✅ api.py found at: {api_path}")
        print(f"   File size: {os.path.getsize(api_path)} bytes")
    else:
        print(f"❌ api.py NOT found at: {api_path}")
    
    # Check azrt2021 directory
    azrt2021_path = os.path.join(current_dir, "azrt2021")
    if os.path.exists(azrt2021_path):
        print(f"✅ azrt2021 directory found")
        init_file = os.path.join(azrt2021_path, "__init__.py")
        if os.path.exists(init_file):
            print(f"✅ azrt2021/__init__.py exists")
        else:
            print(f"⚠️  azrt2021/__init__.py missing (may cause import issues)")
    else:
        print(f"❌ azrt2021 directory NOT found")
    
    print("=" * 70)
    print()

def test_imports():
    """Test if we can import the api module."""
    print("Testing imports...")
    try:
        # Test basic imports first
        import tempfile
        from pathlib import Path
        print("✅ Standard library imports OK")
        
        # Test third-party imports
        try:
            import numpy
            import torch
            print("✅ NumPy and PyTorch imports OK")
        except ImportError as e:
            print(f"⚠️  Warning: {e}")
            print("   This might cause issues later")
        
        # Test FastAPI
        try:
            import fastapi
            import uvicorn
            print("✅ FastAPI and Uvicorn imports OK")
        except ImportError as e:
            print(f"❌ ERROR: {e}")
            return False
        
        # Test our custom modules
        try:
            import api
            print("✅ api module imported successfully")
            if hasattr(api, 'app'):
                print("✅ api.app found")
                return True
            else:
                print("❌ api.app not found")
                return False
        except ImportError as e:
            print(f"❌ ERROR importing api module: {e}")
            print(f"   Traceback:")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ ERROR during import test: {e}")
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    try:
        # Setup environment
        current_dir = setup_environment()
        
        # Print diagnostics
        print_diagnostics(current_dir)
        
        # Verify files exist
        if not verify_files(current_dir):
            sys.exit(1)
        
        # Test imports
        if not test_imports():
            print("\n❌ Import tests failed. Check the errors above.")
            sys.exit(1)
        
        # Import the app
        print("\nImporting application...")
        try:
            import api
            app = api.app
            print("✅ Application imported successfully")
        except Exception as e:
            print(f"❌ FATAL: Failed to import application: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        # Start the server
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        
        print("\n" + "=" * 70)
        print(f"🚀 Starting server on port {port}...")
        print("=" * 70 + "\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
