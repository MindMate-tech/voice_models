# Deploying with Large Model (1.70 GB)

Your model is 1.70 GB, which requires special considerations for deployment.

## 🎯 Recommended Approach: External Model Storage

**Best Practice**: Store the model externally and download it on startup, rather than including it in the repository.

### Why?
- ✅ Faster builds (no need to upload 1.7GB each time)
- ✅ Smaller repository
- ✅ Works on all platforms
- ✅ Easy to update model without redeploying
- ✅ Better version control

## 🏆 Top Recommendations for 1.70 GB Model

### 1. **Railway** ⭐ BEST CHOICE
- **Why**: 
  - $5 free credit/month (usually enough)
  - No sleep on free tier
  - Handles large files well
  - Easy to configure
  - Good storage limits
- **Storage**: 8GB disk space on free tier
- **Build Time**: Generous limits
- **Setup**: Easy GitHub integration
- **Cost**: Free tier usually sufficient

### 2. **Fly.io** ⭐ SECOND CHOICE
- **Why**:
  - 3GB storage per VM (free tier)
  - No sleep
  - Global network
  - Good for large files
- **Storage**: 3GB per VM (free tier)
- **Build Time**: Good limits
- **Setup**: CLI-based, slightly more complex
- **Cost**: Free tier sufficient

### 3. **DigitalOcean App Platform** (Paid)
- **Why**:
  - Reliable for production
  - Good storage options
  - Predictable pricing
- **Storage**: Depends on plan
- **Cost**: Starts at $5/month
- **Best for**: Production use

### 4. **AWS (S3 + Lambda/ECS)**
- **Why**:
  - Store model in S3
  - Download on startup
  - Very scalable
- **Storage**: S3 (pay per GB)
- **Cost**: ~$0.023/GB/month for S3
- **Best for**: Enterprise, high scale

## 📦 Recommended: Store Model Externally

### Option 1: Supabase Storage (Recommended)

Since you're already using Supabase, store the model there:

```python
# In api.py, update load_model() function
def load_model(model_path: Optional[str] = None):
    global model_obj, device
    
    # If model_path is a Supabase URL, download it first
    if model_path and model_path.startswith('http'):
        import urllib.request
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as tmp:
            urllib.request.urlretrieve(model_path, tmp.name)
            model_path = tmp.name
    
    # ... rest of load_model code
```

**Benefits**:
- ✅ Model not in repository
- ✅ Easy to update
- ✅ Fast deployments
- ✅ Works with any hosting platform

### Option 2: AWS S3

```python
import boto3

def download_model_from_s3(bucket, key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, local_path)
```

### Option 3: Google Cloud Storage

```python
from google.cloud import storage

def download_model_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
```

## 🚀 Platform-Specific Recommendations

### For Railway (Recommended)

**Setup**:
1. Upload model to Supabase Storage (or S3)
2. Set environment variable: `MODEL_URL=https://your-project.supabase.co/storage/v1/object/public/models/model.pt`
3. Update `load_model()` to download from URL
4. Deploy to Railway

**Advantages**:
- ✅ Fast builds (no 1.7GB upload)
- ✅ Easy model updates
- ✅ Works on free tier

### For Fly.io

**Setup**:
1. Use `fly volumes` for persistent storage
2. Or download model on startup from external storage
3. Configure volume in `fly.toml`

**Advantages**:
- ✅ Persistent storage option
- ✅ Good free tier
- ✅ Global network

### For Render

**Limitations**:
- ⚠️ Free tier may timeout on large builds
- ⚠️ Limited storage
- ✅ Paid tier works well

**Recommendation**: Use external storage even on Render

## 💡 Implementation: Download Model on Startup

Update your `api.py` to download model from external storage:

```python
import os
import urllib.request
import tempfile

def load_model(model_path: Optional[str] = None):
    global model_obj, device
    
    # Check for MODEL_URL environment variable (for external storage)
    model_url = os.environ.get('MODEL_URL')
    
    if model_url:
        # Download model from external storage
        print(f"Downloading model from: {model_url}")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as tmp:
            urllib.request.urlretrieve(model_url, tmp.name)
            model_path = tmp.name
            print(f"Model downloaded to: {model_path}")
    
    # If model_path is still a URL, download it
    elif model_path and model_path.startswith('http'):
        print(f"Downloading model from URL: {model_path}")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as tmp:
            urllib.request.urlretrieve(model_path, tmp.name)
            model_path = tmp.name
    
    # ... rest of existing load_model code
```

## 📊 Comparison for 1.70 GB Model

| Platform | Storage | Build Time | Free Tier | Recommendation |
|----------|---------|------------|-----------|----------------|
| **Railway** | 8GB | ✅ Good | ✅ Yes | ⭐⭐⭐⭐⭐ Best |
| **Fly.io** | 3GB/VM | ✅ Good | ✅ Yes | ⭐⭐⭐⭐ Great |
| **Render** | Limited | ⚠️ May timeout | ✅ Limited | ⭐⭐⭐ Use external storage |
| **DigitalOcean** | Good | ✅ Good | ❌ Paid | ⭐⭐⭐⭐ Production |
| **AWS** | Unlimited | ✅ Good | ✅ 12mo | ⭐⭐⭐⭐ Enterprise |

## 🎯 Final Recommendation

### Best Choice: **Railway + Supabase Storage**

**Why**:
1. ✅ Railway: Easy, no sleep, good free tier
2. ✅ Supabase Storage: You're already using it
3. ✅ Fast deployments (no 1.7GB in repo)
4. ✅ Easy model updates
5. ✅ Works on free tier

**Setup Steps**:
1. Upload model to Supabase Storage
2. Get public URL
3. Set `MODEL_URL` environment variable in Railway
4. Update `api.py` to download on startup
5. Deploy to Railway

### Alternative: **Fly.io + Volume**

If you prefer to keep model on the server:
1. Use Fly.io volumes for persistent storage
2. Upload model once to volume
3. Mount volume in app
4. Load from volume

## 🔧 Quick Setup: Railway + External Model

1. **Upload model to Supabase**:
   ```bash
   # Use Supabase dashboard or API
   # Get public URL: https://your-project.supabase.co/storage/v1/object/public/models/model.pt
   ```

2. **Update api.py** (code provided above)

3. **Deploy to Railway**:
   - Connect GitHub repo
   - Add environment variable: `MODEL_URL=https://your-project.supabase.co/storage/v1/object/public/models/model.pt`
   - Deploy

4. **Done!** Model downloads on first request

## ⚠️ Important Considerations

### Build Time
- Including 1.7GB in repo: Slow builds (10-20+ minutes)
- External storage: Fast builds (2-5 minutes)

### Repository Size
- Large repos are slow to clone
- GitHub has size limits
- Better to exclude model from repo

### Cold Starts
- First request downloads model (30-60 seconds)
- Subsequent requests are fast
- Consider paid tier for always-on

### Storage Costs
- Supabase: Free tier includes storage
- S3: ~$0.023/GB/month (very cheap)
- Model storage: ~$0.04/month for 1.7GB

## 📝 Action Items

1. ✅ Upload model to Supabase Storage (or S3)
2. ✅ Update `api.py` to download model on startup
3. ✅ Set `MODEL_URL` environment variable
4. ✅ Deploy to Railway (or Fly.io)
5. ✅ Test deployment

## 🆘 Troubleshooting

**Model download fails?**
- Check URL is accessible
- Verify Supabase bucket is public (or use signed URL)
- Check network connectivity in logs

**Build timeout?**
- Use external storage (don't include in repo)
- Increase build timeout if platform allows

**Out of memory?**
- Model loads into RAM
- Consider platform with more RAM
- Or use model quantization

**Slow first request?**
- Normal (downloading 1.7GB)
- Consider keeping model on disk (Fly.io volumes)
- Or use paid tier for always-on

