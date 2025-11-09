# Deploying to Render

This guide will help you deploy the Voice Dementia Detection API to Render.

## Prerequisites

1. A [Render](https://render.com) account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. A trained model in the `azrt2021/pt_files/` directory

## Quick Deployment Steps

### Option 1: Using Render Dashboard (Recommended)

1. **Sign up/Login to Render**
   - Go to https://render.com
   - Sign up or log in

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Select the repository containing this code

3. **Configure the Service**
   - **Name**: `voice-dementia-detection-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `voice_model` (if your repo root is the project root, leave blank)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or choose a paid plan)

4. **Environment Variables** (Optional)
   - `PYTHON_VERSION`: `3.11.0` (or your preferred version)
   - `PORT`: `10000` (Render sets this automatically, but you can specify)

5. **Advanced Settings**
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: Enable if you want automatic deployments on git push

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Wait for the build to complete (usually 5-10 minutes)

### Option 2: Using render.yaml (Infrastructure as Code)

1. **Push render.yaml to your repository**
   - The `render.yaml` file is already in the `voice_model/` directory
   - Commit and push it to your repository

2. **Create Blueprint**
   - In Render dashboard, go to "Blueprints"
   - Click "New Blueprint"
   - Connect your repository
   - Render will detect `render.yaml` and create the service automatically

## Important Configuration

### Root Directory

If your repository structure is:
```
your-repo/
  ├── voice_model/
  │   ├── api.py
  │   ├── requirements.txt
  │   └── ...
  └── README.md
```

Set **Root Directory** to: `voice_model`

If your repository root IS the voice_model directory:
```
your-repo/
  ├── api.py
  ├── requirements.txt
  └── ...
```

Leave **Root Directory** blank.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn api:app --host 0.0.0.0 --port $PORT
```

**Important**: Use `$PORT` environment variable (Render sets this automatically)

### Health Check

The API has a health check endpoint at `/health`. Configure it in Render:
- **Health Check Path**: `/health`

## Environment Variables

You can set these in Render dashboard under "Environment":

| Variable | Value | Required | Description |
|----------|-------|----------|-------------|
| `PYTHON_VERSION` | `3.11.0` | No | Python version (default: 3.11.0) |
| `PORT` | `10000` | No | Port (Render sets this automatically) |

## Model Files

**Important**: Your trained model files must be in the repository or uploaded separately.

### Option 1: Include in Git (for small models)
- Commit model files to `azrt2021/pt_files/`
- Push to repository
- Model will be available after deployment

### Option 2: Upload after deployment
- Deploy the API first
- Use Render's file system or external storage (S3, etc.)
- Update model path in code if needed

### Option 3: Use external storage
- Store models in S3, Supabase Storage, etc.
- Update `load_model()` function to download from external storage
- Add environment variables for storage credentials

## Post-Deployment

### 1. Test the Deployment

Once deployed, test your API:

```bash
# Health check
curl https://your-service.onrender.com/health

# Test prediction (replace with your actual audio file)
curl -X POST "https://your-service.onrender.com/predict" \
  -F "file=@audio.mp3"
```

### 2. Get Your API URL

Your API will be available at:
```
https://your-service-name.onrender.com
```

Or with a custom domain if configured.

### 3. Update Documentation

Update any client code or documentation with the new API URL.

## Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError` or missing dependencies
- **Solution**: Ensure `requirements.txt` includes all dependencies
- Check build logs in Render dashboard

**Error**: `torch` installation fails
- **Solution**: PyTorch can be large. Consider using CPU-only version:
  ```txt
  torch>=1.10.1 --index-url https://download.pytorch.org/whl/cpu
  ```

### Service Crashes

**Error**: `Port already in use`
- **Solution**: Ensure start command uses `$PORT` environment variable

**Error**: `Model not found`
- **Solution**: 
  - Verify model files are in repository
  - Check file paths are correct
  - Check build logs for file structure

### Slow Cold Starts

**Issue**: First request takes a long time
- **Solution**: 
  - Model loading happens on first request
  - Consider using a paid plan for better performance
  - Or pre-load model on startup (already implemented)

### Memory Issues

**Error**: Out of memory
- **Solution**:
  - Free tier has limited memory
  - Consider upgrading to a paid plan
  - Or optimize model loading

## Free Tier Limitations

- **Sleeps after 15 minutes of inactivity**: First request after sleep will be slow
- **Limited resources**: May need paid plan for production use
- **Build time limits**: Large dependencies may timeout

## Upgrading to Paid Plan

For production use, consider upgrading:
- No sleep on inactivity
- More resources (CPU, RAM)
- Better performance
- Custom domains
- More concurrent requests

## Custom Domain

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Follow DNS configuration instructions

## Monitoring

Render provides:
- **Logs**: View real-time logs in dashboard
- **Metrics**: CPU, memory, request metrics
- **Alerts**: Set up alerts for errors

## Continuous Deployment

Render automatically deploys when you push to your connected branch:
1. Push code to repository
2. Render detects changes
3. Builds and deploys automatically
4. Your API is updated

## Security Considerations

1. **API Keys**: Don't commit secrets to repository
2. **CORS**: Update CORS settings for production
3. **Rate Limiting**: Consider adding rate limiting
4. **Authentication**: Add API key authentication if needed
5. **HTTPS**: Render provides HTTPS by default

## Example Client Code

After deployment, update your client code:

```python
import requests

# Your Render API URL
API_URL = "https://your-service.onrender.com"

# Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# Predict from file
with open("audio.mp3", "rb") as f:
    response = requests.post(
        f"{API_URL}/predict",
        files={"file": f}
    )
    print(response.json())

# Predict from Supabase URL
response = requests.post(
    f"{API_URL}/predict/url",
    json={"url": "https://your-project.supabase.co/storage/v1/object/public/audio/file.mp3"}
)
print(response.json())
```

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Check Render dashboard logs for detailed error messages

