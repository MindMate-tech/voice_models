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
    
    # Add current directory to Python path (MUST be first)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Also add parent directory in case Render has weird path structure
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path and os.path.exists(parent_dir):
        sys.path.insert(0, parent_dir)
    
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
    print(f"Python path (first 5):")
    for i, path in enumerate(sys.path[:5], 1):
        print(f"  {i}. {path}")
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
