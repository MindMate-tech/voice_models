# Render Deployment - Quick Start

## 🚀 5-Minute Deployment Guide

### Step 1: Prepare Your Repository

1. **Ensure all files are committed:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push
   ```

2. **Verify these files exist:**
   - ✅ `api.py`
   - ✅ `requirements.txt`
   - ✅ `render.yaml` (optional, but recommended)
   - ✅ `runtime.txt` (optional)

### Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Sign up or log in

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your Git repository (GitHub/GitLab/Bitbucket)

3. **Configure Service**

   **Basic Settings:**
   - **Name**: `voice-dementia-api` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `voice_model` ⚠️ **IMPORTANT** (if your repo structure has voice_model folder)
   
   **Build & Start:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   
   **Plan:**
   - **Free** (for testing) or **Starter** (for production)

4. **Advanced Settings** (Optional)
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: ✅ Yes (deploys on every push)

5. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build to complete

### Step 3: Test Your Deployment

Once deployed, you'll get a URL like:
```
https://voice-dementia-api.onrender.com
```

**Test it:**
```bash
# Health check
curl https://your-service.onrender.com/health

# Test prediction
curl -X POST "https://your-service.onrender.com/predict" \
  -F "file=@audio.mp3"
```

## ⚠️ Important Notes

### Root Directory

**If your repo structure is:**
```
your-repo/
  ├── voice_model/     ← API code here
  │   ├── api.py
  │   └── requirements.txt
  └── README.md
```

**Set Root Directory to:** `voice_model`

**If your repo root IS voice_model:**
```
your-repo/  ← This IS voice_model
  ├── api.py
  └── requirements.txt
```

**Leave Root Directory blank**

### Model Files

Your trained models need to be in the repository:
- Models should be in `azrt2021/pt_files/`
- Commit and push them to your repo
- Or use external storage (see RENDER_DEPLOYMENT.md)

### Free Tier Limitations

- ⏰ **Sleeps after 15 min inactivity** - First request after sleep is slow
- 💾 **Limited resources** - May need upgrade for production
- ⏱️ **Build timeouts** - Large dependencies may timeout

## 🎯 Quick Checklist

Before deploying:
- [ ] Code pushed to Git repository
- [ ] `requirements.txt` is up to date
- [ ] Model files are in repository (or external storage configured)
- [ ] Root directory is set correctly
- [ ] Start command uses `$PORT` environment variable

After deploying:
- [ ] Health check works: `/health`
- [ ] API responds to requests
- [ ] Model loads successfully
- [ ] Test with a real audio file

## 🆘 Troubleshooting

**Build fails?**
- Check build logs in Render dashboard
- Ensure all dependencies in `requirements.txt`
- Check Python version compatibility

**Service crashes?**
- Check logs in Render dashboard
- Verify model files exist
- Check start command uses `$PORT`

**Slow first request?**
- Normal on free tier (cold start)
- Model loads on first request
- Consider paid plan

## 📚 More Information

See `RENDER_DEPLOYMENT.md` for:
- Detailed configuration
- Environment variables
- Custom domains
- Production optimizations
- Security best practices

