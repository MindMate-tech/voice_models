# What Files Are Needed for Deployment?

## ✅ Files You NEED for Deployment

### Essential Files
- ✅ `api.py` - Main API application
- ✅ `requirements.txt` - Python dependencies
- ✅ `azrt2021/model.py` - Model wrapper class
- ✅ `azrt2021/tcn.py` - TCN architecture
- ✅ `azrt2021/mfcc.py` - MFCC feature extraction
- ✅ `azrt2021/data.py` - Data loading utilities
- ✅ `preprocess_audio.py` - Audio preprocessing
- ✅ Model file (`.pt`) - **ONLY if not using external storage**

### Configuration Files (Optional but Recommended)
- ✅ `render.yaml` / `railway.json` - Platform config
- ✅ `runtime.txt` - Python version
- ✅ `Procfile` - Start command
- ✅ `Dockerfile` - If using Docker

## ❌ Files You DON'T Need for Deployment

### Training Data (NOT needed)
- ❌ `data/` folder - Training audio files
- ❌ `nodementia/` folder - Training audio files
- ❌ `data/mfcc_features/` - Preprocessed training features
- ❌ `data/csv_files/dataset.csv` - Training dataset
- ❌ `csv_files/` - Training CSVs

### Training Scripts (NOT needed)
- ❌ `azrt2021/train.py` - Training script
- ❌ `convert_all_data.py` - Data conversion script
- ❌ `auto_convert_audio.py` - Audio conversion script
- ❌ `azrt2021/results/` - Training results

### Development Files (NOT needed)
- ❌ `venv/` - Virtual environment
- ❌ `__pycache__/` - Python cache
- ❌ `.vscode/`, `.idea/` - IDE files
- ❌ `*.md` - Documentation (optional, can include if small)

## 📊 File Size Impact

### With Training Data
- Model: 1.70 GB
- Training data: ~500 MB - 2 GB+ (audio files)
- MFCC features: ~200 MB - 1 GB
- **Total**: 2.4 GB - 4.7 GB+ ⚠️

### Without Training Data (Recommended)
- Model: 1.70 GB (or external storage)
- Code: ~5-10 MB
- **Total**: ~10 MB (if model in external storage) ✅

## 🎯 Best Practice: External Model Storage

### Recommended Setup
1. **Store model externally** (Supabase, S3, etc.)
2. **Exclude from repository**:
   - Model files (`azrt2021/pt_files/`)
   - Training data (`data/`, `nodementia/`)
   - Training features (`data/mfcc_features/`)
3. **Include only**:
   - API code
   - Model architecture files
   - Dependencies

### Benefits
- ✅ **Fast deployments** (2-5 min vs 15-20+ min)
- ✅ **Small repository** (~10 MB vs 2-4 GB+)
- ✅ **Easy updates** (update model without redeploying)
- ✅ **No build timeouts**
- ✅ **Works on free tiers**

## 📝 Deployment Checklist

### Before Deployment
- [ ] Model uploaded to external storage (Supabase/S3)
- [ ] `MODEL_URL` environment variable set
- [ ] Training data excluded (`.renderignore`, `.dockerignore`)
- [ ] Model files excluded (if using external storage)
- [ ] Only essential files in repository

### Files to Include
```
voice_model/
├── api.py                    ✅ Essential
├── requirements.txt          ✅ Essential
├── preprocess_audio.py      ✅ Essential
├── azrt2021/
│   ├── model.py             ✅ Essential
│   ├── tcn.py               ✅ Essential
│   ├── mfcc.py              ✅ Essential
│   ├── data.py              ✅ Essential
│   └── (other .py files)    ✅ Essential
├── render.yaml              ✅ Config
├── runtime.txt              ✅ Config
└── Procfile                 ✅ Config
```

### Files to Exclude
```
voice_model/
├── data/                    ❌ Training data
├── nodementia/              ❌ Training data
├── azrt2021/pt_files/       ❌ Model (if external)
├── azrt2021/results/        ❌ Training results
├── venv/                    ❌ Virtual env
└── *.md                     ❌ Docs (optional)
```

## 🔧 How to Exclude Files

### Option 1: .renderignore (Render)
Already created! Files listed in `.renderignore` are excluded.

### Option 2: .dockerignore (Docker)
Already created! Files listed in `.dockerignore` are excluded.

### Option 3: .gitignore (Git)
Add to `.gitignore` if you want to exclude from repository entirely:
```
# Training data
data/
nodementia/
azrt2021/results/

# Model files (if using external storage)
azrt2021/pt_files/
```

### Option 4: Platform Settings
Most platforms (Railway, Fly.io) respect `.gitignore` or have their own ignore files.

## 💡 Why This Matters

### Without Excluding Training Data
- ⏱️ **Slow builds**: 15-20+ minutes
- 💾 **Large repository**: 2-4 GB+
- ⚠️ **Build timeouts**: May fail on free tiers
- 🐌 **Slow clones**: Git operations are slow

### With External Model Storage
- ⚡ **Fast builds**: 2-5 minutes
- 📦 **Small repository**: ~10 MB
- ✅ **No timeouts**: Works on free tiers
- 🚀 **Fast deployments**: Quick iterations

## 🎯 Summary

**For deployment, you ONLY need:**
1. ✅ Trained model file (1.70 GB) - **Store externally**
2. ✅ API code (~5-10 MB)
3. ✅ Dependencies (installed during build)

**You DON'T need:**
- ❌ Training audio files
- ❌ Training MFCC features
- ❌ Training CSV files
- ❌ Training scripts
- ❌ Training results

**Result**: Deployment goes from **2-4 GB+** to **~10 MB** (if model is external)!

