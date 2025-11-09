# Fixing "ModuleNotFoundError: No module named 'src'" on Render

## Problem

When deploying to Render, you get:
```
ModuleNotFoundError: No module named 'src'
```

This error occurs because Render deploys to `/opt/render/project/src/`, and when uvicorn tries to import the `api` module, Python's import system can't resolve it correctly.

## Solution

This error typically occurs due to:
1. Missing `__init__.py` files making packages
2. Incorrect import paths
3. Render's build environment path issues
4. Python path not including the current working directory

## Fixes Applied

### 1. Updated `render.yaml` start command (PRIMARY FIX)
- Changed from: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Changed to: `PYTHONPATH=. python -m uvicorn api:app --host 0.0.0.0 --port $PORT`
- This ensures the current directory is in Python's module search path
- Using `python -m uvicorn` ensures proper module resolution

### 2. Created `azrt2021/__init__.py`
- Makes `azrt2021` a proper Python package
- Allows proper module imports

### 3. Fixed imports in `azrt2021/model.py`
- Changed from bare imports (`from tcn import TCN`) 
- To relative imports with fallback (`from .tcn import TCN`)
- Prevents module resolution issues

### 4. Improved path setup in `api.py`
- Added both current directory and azrt2021 to sys.path
- Ensures modules can be found regardless of working directory

## Verification

After these fixes, the imports should work:
- ✅ `from azrt2021.model import Model`
- ✅ `from azrt2021.tcn import TCN`
- ✅ `from azrt2021.mfcc import MFCC_Extractor`

## If Error Persists

### Check Render Build Logs

1. Go to Render dashboard
2. Click on your service
3. Check "Logs" tab
4. Look for the exact import that's failing

### Common Issues

1. **Missing file**: Ensure all Python files are committed to Git
2. **Wrong root directory**: Check if Root Directory is set correctly in Render
3. **Python version**: Ensure `runtime.txt` specifies correct Python version

### Alternative: Use Absolute Imports

If relative imports still fail, you can modify imports to be fully absolute:

```python
# In azrt2021/model.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azrt2021.tcn import TCN
from azrt2021.data import collate_fn
from azrt2021.misc import calc_performance_metrics, show_performance_metrics
```

## Testing Locally

Before deploying, test the imports locally:

```bash
cd voice_model
source venv/bin/activate
python -c "from azrt2021.model import Model; print('✅ Import successful')"
```

If this works locally but fails on Render, it's likely a path/environment issue.

