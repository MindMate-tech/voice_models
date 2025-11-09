#!/usr/bin/env python3
"""
FastAPI application for voice dementia detection.

This API accepts audio files (MP3, WAV, etc.) and returns dementia probability analysis.

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000
    or
    python api.py
"""

import os
import sys

# CRITICAL: Set up Python path FIRST, before any other imports
# This fixes the "No module named 'src'" error on Render
current_dir = os.path.dirname(os.path.abspath(__file__))

# CRITICAL: Remove parent 'src' directory from Python path to prevent import errors
# Render deploys to /opt/render/project/src/voice_model/
# We keep /opt/render/project/src/voice_model/ but remove /opt/render/project/src/
# This prevents Python from trying to import 'src' as a module
filtered_path = []
for p in sys.path:
    # Keep the current directory (voice_model) even if it contains 'src' in the path
    if p == current_dir:
        filtered_path.append(p)
    # Keep paths that don't contain 'src'
    elif 'src' not in p:
        filtered_path.append(p)
    # Remove paths that end with 'src' (these would cause 'src' module import errors)
    elif not p.endswith('src') and not p.endswith('src/'):
        # Only keep if it's related to our current directory
        if current_dir in p or p in current_dir:
            filtered_path.append(p)
sys.path = filtered_path

# Add current directory to Python path (MUST be first)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import tempfile
from pathlib import Path
from typing import Optional

# Check if running in virtual environment and dependencies are available
try:
    import numpy as np
    import torch
except ImportError as e:
    print("=" * 60)
    print("❌ ERROR: Missing required dependencies")
    print("=" * 60)
    print(f"Missing module: {e}")
    print()
    print("Please ensure you:")
    print("1. Activate the virtual environment:")
    print("   source venv/bin/activate")
    print()
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("Or use the start script:")
    print("   ./start_api.sh")
    print("=" * 60)
    sys.exit(1)

from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Add azrt2021 to path for proper module resolution
# current_dir is already set above and added to sys.path
azrt2021_dir = os.path.join(current_dir, 'azrt2021')

# Add azrt2021 directory to path if not already there
# NOTE: We only add current_dir and azrt2021_dir, NOT parent directories
# This prevents Python from trying to import 'src' as a module
if azrt2021_dir not in sys.path and os.path.exists(azrt2021_dir):
    sys.path.insert(0, azrt2021_dir)

# Import modules with error handling
try:
    from azrt2021.model import Model
    from azrt2021.tcn import TCN
    from preprocess_audio import load_audio_file
    from azrt2021.mfcc import MFCC_Extractor
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"azrt2021 directory: {azrt2021_dir}")
    print(f"Python path: {sys.path[:5]}")  # Show first 5 paths
    print(f"Files in current_dir: {os.listdir(current_dir) if os.path.exists(current_dir) else 'NOT FOUND'}")
    print(f"Files in azrt2021_dir: {os.listdir(azrt2021_dir) if os.path.exists(azrt2021_dir) else 'NOT FOUND'}")
    raise

app = FastAPI(
    title="Voice Dementia Detection API",
    description="API for analyzing voice audio files to detect signs of dementia",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable (loaded on startup)
model_obj = None

# Device detection - default to CPU for stability, allow override via environment variable
if os.environ.get('DEVICE'):
    device = os.environ.get('DEVICE')
    print(f"📱 Using device from environment: {device}")
else:
    # Default to CPU for stability (can be overridden to 'cuda:0' if needed)
    device = 'cpu'
    print(f"📱 Using CPU (set DEVICE=cuda:0 environment variable to use GPU)")


# Pydantic models for request bodies
class URLRequest(BaseModel):
    url: str


def load_model(model_path: Optional[str] = None):
    """
    Load the trained model.
    
    Supports loading from:
    - Local file path
    - URL (Supabase, S3, etc.) - downloads automatically
    - Environment variable MODEL_URL
    
    Parameters:
    -----------
    model_path : str, optional
        Path to model file or URL. If None, checks MODEL_URL env var or local files.
    """
    global model_obj, device
    
    # Check for MODEL_URL environment variable (for external storage like Supabase)
    model_url = os.environ.get('MODEL_URL')
    
    # If MODEL_URL is set, use it (takes priority)
    if model_url:
        print(f"📥 Model URL found in environment: {model_url}")
        model_path = model_url
    
    # If model_path is a URL, download it first
    if model_path and (model_path.startswith('http://') or model_path.startswith('https://')):
        print(f"📥 Downloading model from URL: {model_path}")
        import urllib.request
        import tempfile
        
        # Create temp file for downloaded model
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as tmp:
            try:
                # Download with progress indication
                print("   Downloading... (this may take a minute for large models)")
                urllib.request.urlretrieve(model_path, tmp.name)
                model_path = tmp.name
                file_size = os.path.getsize(model_path) / (1024 * 1024)  # Size in MB
                print(f"✅ Model downloaded successfully ({file_size:.2f} MB)")
            except Exception as e:
                os.unlink(tmp.name)  # Clean up on error
                raise Exception(f"Failed to download model from URL: {str(e)}")
    
    # Find model file if not provided
    if model_path is None or (not model_path.startswith('http') and not os.path.isfile(model_path)):
        pt_files_dir = Path(__file__).parent / 'azrt2021' / 'pt_files'
        if pt_files_dir.exists():
            pt_files = []
            for root, dirs, files in os.walk(pt_files_dir):
                for file in files:
                    if file.endswith('.pt') and 'tmp' not in file:
                        pt_files.append(os.path.join(root, file))
            
            if pt_files:
                pt_files.sort(key=os.path.getmtime, reverse=True)
                model_path = pt_files[0]
                print(f"📁 Using most recent local model: {model_path}")
            else:
                raise FileNotFoundError(
                    f"No trained model found. Please:\n"
                    f"  1. Set MODEL_URL environment variable, or\n"
                    f"  2. Place model files in {pt_files_dir}, or\n"
                    f"  3. Provide model_path parameter"
                )
        else:
            raise FileNotFoundError(
                f"Model directory not found: {pt_files_dir}. "
                f"Please set MODEL_URL environment variable or provide model_path."
            )
    
    # Verify local file exists (if not a URL)
    if not model_path.startswith('http') and not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    print(f"🔄 Loading model from: {model_path}")
    
    # Initialize model
    n_concat = 10
    neural_network = TCN(device)
    model_obj = Model(n_concat=n_concat, device=device, nn=neural_network)
    model_obj.load_model(model_path)
    
    # CRITICAL: Explicitly move model to the correct device
    # This ensures models saved on GPU are properly moved to CPU
    model_obj.to(device)
    model_obj.nn.eval()
    
    # Ensure all parameters are on the correct device and disable gradients
    for param in model_obj.nn.parameters():
        param.requires_grad = False
    
    print(f"✅ Model loaded successfully on device: {device}")


def predict_voice_from_audio(audio_path: str) -> dict:
    """
    Predict dementia probability from an audio file.
    
    Parameters:
    -----------
    audio_path : str
        Path to audio file
    
    Returns:
    --------
    dict: Analysis results with probabilities and interpretation
    """
    if model_obj is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please ensure a model is available.")
    
    try:
        # Load audio
        audio = load_audio_file(audio_path)
        audio_length_seconds = len(audio) / 16000
        
        # Extract MFCC features
        mfcc_extractor = MFCC_Extractor(
            samplerate=16000,
            winlen=0.025,
            winstep=0.01,
            numcep=13,
            nfilt=26,
            device=device
        )
        
        audio_batch = audio.reshape(1, -1)
        mfcc_features = mfcc_extractor(audio_batch)[0]
        
        # Ensure MFCC features are numpy array (CPU) or convert if needed
        if isinstance(mfcc_features, torch.Tensor):
            # Convert tensor to numpy if on wrong device
            if mfcc_features.device.type != 'cpu':
                mfcc_features = mfcc_features.cpu().numpy()
            else:
                mfcc_features = mfcc_features.numpy()
        elif not isinstance(mfcc_features, np.ndarray):
            mfcc_features = np.array(mfcc_features)
        
        # Prepare data for model
        mfcc_list = [mfcc_features]
        model_obj.nn.reformat(mfcc_list, 10)
        
        # Get prediction
        with torch.no_grad():
            scores = model_obj.nn.get_scores(mfcc_list)
            probs = torch.softmax(scores, dim=1)
            # NOTE: Labels are flipped (class 0 = Dementia, class 1 = Normal)
            dementia_prob = probs[0][0].item()
            normal_prob = probs[0][1].item()
        
        # Determine result
        if dementia_prob > 0.5:
            result = "dementia_detected"
            confidence = dementia_prob
            message = f"High dementia probability detected ({dementia_prob*100:.2f}%). This suggests possible signs of dementia in the voice."
        else:
            result = "normal"
            confidence = normal_prob
            message = f"Normal voice detected ({normal_prob*100:.2f}% confidence). The voice appears to be within normal range."
        
        return {
            "status": "success",
            "result": result,
            "probabilities": {
                "normal": round(normal_prob, 4),
                "normal_percentage": round(normal_prob * 100, 2),
                "dementia": round(dementia_prob, 4),
                "dementia_percentage": round(dementia_prob * 100, 2)
            },
            "confidence": round(confidence, 4),
            "message": message,
            "audio_info": {
                "length_seconds": round(audio_length_seconds, 2),
                "mfcc_features_shape": list(mfcc_features.shape)
            },
            "note": "This is a screening tool and should not replace professional medical diagnosis."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    try:
        load_model()
    except Exception as e:
        print(f"⚠️  Warning: Could not load model on startup: {e}")
        print("   Model will be loaded on first request.")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Voice Dementia Detection API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": model_obj is not None,
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/predict": "Upload audio file for analysis (POST)",
            "/docs": "Interactive API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model_obj is not None,
        "device": device
    }


@app.post("/predict")
async def predict(
    file: UploadFile = File(..., description="Audio file (MP3, WAV, FLAC, etc.)")
):
    """
    Analyze an audio file for dementia detection.
    
    Parameters:
    -----------
    file : UploadFile
        Audio file to analyze (MP3, WAV, FLAC, M4A, OGG, AAC)
    
    Returns:
    --------
    JSON response with analysis results including:
    - result: "normal" or "dementia_detected"
    - probabilities: normal and dementia probabilities
    - confidence: confidence level
    - message: interpretation message
    - audio_info: audio file metadata
    """
    # Validate file type
    allowed_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    # Load model if not already loaded
    if model_obj is None:
        try:
            load_model()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Model not available: {str(e)}"
            )
    
    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        try:
            # Write uploaded file to temp file
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            # Analyze the audio
            result = predict_voice_from_audio(tmp_file_path)
            
            return JSONResponse(content=result)
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


@app.post("/predict/url")
async def predict_from_url(
    request: URLRequest,
    authorization: Optional[str] = Header(None, alias="Authorization")
):
    """
    Analyze an audio file from a URL (supports Supabase and other cloud storage).
    
    Parameters:
    -----------
    request : URLRequest
        JSON body with 'url' field containing the audio file URL
    authorization : str, optional
        Authorization header (Bearer token) for authenticated Supabase URLs
        
    Request Body:
    ------------
    {
        "url": "https://your-project.supabase.co/storage/v1/object/public/bucket/audio.mp3"
    }
        
    Examples:
    --------
    - Public Supabase URL: https://your-project.supabase.co/storage/v1/object/public/bucket/audio.mp3
    - Signed URL: https://your-project.supabase.co/storage/v1/object/sign/bucket/audio.mp3?token=...
    - Any public URL: https://example.com/audio.mp3
    """
    url = request.url
    import urllib.request
    import urllib.parse
    
    # Load model if not already loaded
    if model_obj is None:
        try:
            load_model()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Model not available: {str(e)}"
            )
    
    # Download file from URL
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(url).suffix) as tmp_file:
        tmp_file_path = tmp_file.name
        try:
            # Create request with optional authorization header
            req = urllib.request.Request(url)
            
            # Add authorization header if provided (for Supabase authenticated URLs)
            if authorization:
                if authorization.startswith("Bearer "):
                    req.add_header("Authorization", authorization)
                else:
                    req.add_header("Authorization", f"Bearer {authorization}")
            
            # Add user agent to avoid blocking
            req.add_header("User-Agent", "Voice-Dementia-Detection-API/1.0")
            
            # Download the file
            with urllib.request.urlopen(req, timeout=30) as response:
                # Check content type if available
                content_type = response.headers.get("Content-Type", "")
                if content_type and not any(ext in content_type.lower() for ext in ['audio', 'octet-stream', 'binary']):
                    # Not a critical check, but log if unexpected
                    pass
                
                # Write to temp file
                with open(tmp_file_path, 'wb') as f:
                    f.write(response.read())
            
            # Analyze the audio
            result = predict_voice_from_audio(tmp_file_path)
            
            return JSONResponse(content=result)
        
        except urllib.error.HTTPError as e:
            if e.code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Unauthorized: Invalid or missing authentication token. For Supabase, provide a valid Bearer token."
                )
            elif e.code == 403:
                raise HTTPException(
                    status_code=403,
                    detail="Forbidden: Access denied. Check if the file is public or use a signed URL with proper authentication."
                )
            elif e.code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="File not found at the provided URL."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error downloading file: HTTP {e.code} - {e.reason}"
                )
        except urllib.error.URLError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error accessing URL: {str(e)}. Check if the URL is valid and accessible."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file from URL: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


if __name__ == "__main__":
    # Run the API server
    # Use PORT environment variable if available (for Render, Heroku, etc.)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

