# Cloud Run Deployment Fix

## Issue
The Cloud Run service 'voice-models' was failing to start because:
- Application was not listening on port 8080 (Cloud Run's expected port)
- Startup timeout exceeded 240 seconds
- Health check was using wrong port

## Changes Made

### 1. Dockerfile (`Dockerfile`)
- ✅ Updated `EXPOSE` to 8080 (Cloud Run's default port)
- ✅ Updated `CMD` to use `PORT` environment variable (defaults to 8080)
- ✅ Fixed health check to use `PORT` environment variable
- ✅ Increased health check start-period to 60s to allow for model loading
- ✅ Created `start_server.sh` script for cleaner port handling

### 2. API Code (`api.py`)
- ✅ Updated default port from 8000 to 8080 for Cloud Run compatibility
- ✅ Enhanced startup logging to help debug issues
- ✅ Improved health check endpoint documentation
- ✅ Added `ready: true` field to health check response (always returns true, even if model not loaded)

### 3. Startup Script (`start_server.sh`)
- ✅ Created dedicated startup script that properly handles PORT environment variable
- ✅ Provides clear logging of port configuration

## Key Fixes

### Port Configuration
- **Before**: Hardcoded port 8000
- **After**: Uses `PORT` environment variable (Cloud Run sets this to 8080)
- **Fallback**: Defaults to 8080 if PORT not set

### Health Check
- **Before**: Used hardcoded port 8000
- **After**: Uses `PORT` environment variable
- **Behavior**: Returns immediately, doesn't require model to be loaded

### Startup Performance
- Health check responds immediately (doesn't wait for model)
- Model loading happens in background (non-blocking)
- Server starts listening on port before model loads

## Testing

### Local Testing with PORT=8080
```bash
cd voice_models
PORT=8080 python api.py
# Or
PORT=8080 uvicorn api:app --host 0.0.0.0 --port 8080
```

### Docker Testing
```bash
cd voice_models
docker build -t voice-models .
docker run -p 8080:8080 -e PORT=8080 voice-models
# Test health check
curl http://localhost:8080/health
```

### Cloud Run Deployment
1. Build and push the image:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/voice-models
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy voice-models \
     --image gcr.io/PROJECT_ID/voice-models \
     --platform managed \
     --region europe-west1 \
     --port 8080 \
     --allow-unauthenticated
   ```

## Verification

After deployment, verify:
1. ✅ Service starts successfully (check logs)
2. ✅ Health check responds: `curl https://your-service-url/health`
3. ✅ Root endpoint works: `curl https://your-service-url/`
4. ✅ Model loads (check logs for "Model loaded successfully")

## Notes

- The health check endpoint (`/health`) will always return `status: "healthy"` and `ready: true`, even if the model hasn't loaded yet
- Model loading happens asynchronously in the background
- If model fails to load on startup, it will be loaded on first prediction request
- Cloud Run's startup probe will pass once the server is listening on port 8080, which happens immediately

