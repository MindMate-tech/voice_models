# Voice Dementia Detection API

FastAPI application for analyzing voice audio files to detect signs of dementia.

## Installation

1. Install dependencies:
```bash
cd voice_model
source venv/bin/activate
pip install fastapi uvicorn[standard] python-multipart
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Running the API

### Start the server:

**IMPORTANT:** Always activate the virtual environment first!

```bash
cd voice_model
source venv/bin/activate

# Option 1: Using the start script (RECOMMENDED)
./start_api.sh

# Option 2: Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Using Python
python api.py
```

**Note:** If you get `ModuleNotFoundError: No module named 'torch'`, make sure:
1. You've activated the virtual environment: `source venv/bin/activate`
2. Dependencies are installed: `pip install -r requirements.txt`

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Root Endpoint
**GET** `/`

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Voice Dementia Detection API",
  "version": "1.0.0",
  "status": "running",
  "model_loaded": true,
  "endpoints": {...}
}
```

### 2. Health Check
**GET** `/health`

Check API and model status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### 3. Predict (File Upload)
**POST** `/predict`

Upload an audio file for analysis.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the audio file

**Supported formats:** MP3, WAV, FLAC, M4A, OGG, AAC

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/audio.mp3"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/predict"
files = {"file": open("audio.mp3", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "status": "success",
  "result": "normal",
  "probabilities": {
    "normal": 0.7234,
    "normal_percentage": 72.34,
    "dementia": 0.2766,
    "dementia_percentage": 27.66
  },
  "confidence": 0.7234,
  "message": "Normal voice detected (72.34% confidence). The voice appears to be within normal range.",
  "audio_info": {
    "length_seconds": 45.23,
    "mfcc_features_shape": [4523, 13]
  },
  "note": "This is a screening tool and should not replace professional medical diagnosis."
}
```

**Result values:**
- `"normal"`: Voice appears normal (dementia probability < 50%)
- `"dementia_detected"`: Possible signs of dementia (dementia probability > 50%)

### 4. Predict from URL
**POST** `/predict/url`

Analyze an audio file from a URL.

**Request:**
```json
{
  "url": "https://example.com/audio.mp3"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/predict/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/audio.mp3"}'
```

## Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test the API directly from these pages by uploading files.

## Response Format

### Success Response
```json
{
  "status": "success",
  "result": "normal" | "dementia_detected",
  "probabilities": {
    "normal": 0.0-1.0,
    "normal_percentage": 0.0-100.0,
    "dementia": 0.0-1.0,
    "dementia_percentage": 0.0-100.0
  },
  "confidence": 0.0-1.0,
  "message": "Human-readable interpretation",
  "audio_info": {
    "length_seconds": float,
    "mfcc_features_shape": [int, int]
  },
  "note": "Medical disclaimer"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Example Usage

### Python Client
```python
import requests

# Upload file
url = "http://localhost:8000/predict"
with open("test_audio.mp3", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    
result = response.json()
print(f"Result: {result['result']}")
print(f"Dementia Probability: {result['probabilities']['dementia_percentage']}%")
print(f"Normal Probability: {result['probabilities']['normal_percentage']}%")
```

### JavaScript/TypeScript Client
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/predict', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data.result);
  console.log('Dementia Probability:', data.probabilities.dementia_percentage + '%');
});
```

### cURL
```bash
# Test with a local file
curl -X POST "http://localhost:8000/predict" \
  -F "file=@/path/to/audio.mp3"

# Save response to file
curl -X POST "http://localhost:8000/predict" \
  -F "file=@/path/to/audio.mp3" \
  -o response.json
```

## Configuration

### Change Port
```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

### Production Deployment
For production, use a production ASGI server:

```bash
# Install gunicorn with uvicorn workers
pip install gunicorn

# Run with multiple workers
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables
You can set these environment variables:
- `MODEL_PATH`: Path to specific model file (optional)
- `DEVICE`: Device to use (`cpu` or `cuda:0`)

## Troubleshooting

### "Model not loaded"
- Ensure you have trained a model first
- Check that model files exist in `azrt2021/pt_files/`
- The API will try to load the most recent model automatically

### "Unsupported file type"
- Make sure your audio file is one of: MP3, WAV, FLAC, M4A, OGG, AAC
- Check file extension is correct

### "Error processing audio"
- Verify the audio file is not corrupted
- Check that `librosa` and `soundfile` are installed
- Ensure the audio file can be loaded

### Port already in use
```bash
# Use a different port
uvicorn api:app --host 0.0.0.0 --port 8001
```

## Security Notes

- The API accepts files from any origin (CORS enabled for all)
- For production, consider:
  - Adding authentication
  - Limiting file size
  - Restricting CORS origins
  - Adding rate limiting
  - Using HTTPS

## Model Information

- The API automatically loads the most recent trained model
- Model is loaded once on startup (or first request)
- Supports both CPU and CUDA devices
- Uses the same model architecture as the training script

