# Fix for "/src/" Path Issue on Render

## The Problem

Render deploys your code to `/opt/render/project/src/`, and with `rootDir: voice_model`, your actual code is at:
```
/opt/render/project/src/voice_model/
```

When Python tries to import modules, it might look in `/opt/render/project/src/` and try to import `src` as a module, causing:
```
ModuleNotFoundError: No module named 'src'
```

## The Solution

We've updated both `run.py` and `api.py` to:

1. **Filter out problematic paths**: Remove any paths ending with `src` or `src/` from `sys.path`
2. **Keep only necessary paths**: Only keep:
   - The current directory (`/opt/render/project/src/voice_model/`)
   - The `azrt2021` subdirectory
   - Standard Python library paths
3. **Never add parent directories**: We explicitly avoid adding parent directories that contain `src`

## What Changed

### In `run.py`:
- Added path filtering to remove `src` directories from Python path
- Only keeps paths that are necessary for imports
- Provides diagnostics showing which paths contain 'src'

### In `api.py`:
- Same path filtering applied at the very beginning
- Ensures imports work correctly even if `run.py` didn't run first

## How It Works

**Before (Problematic)**:
```python
sys.path = [
    '/opt/render/project/src/',  # ❌ This causes 'src' module import errors
    '/opt/render/project/src/voice_model/',  # ✅ This is what we want
    ...
]
```

**After (Fixed)**:
```python
sys.path = [
    '/opt/render/project/src/voice_model/',  # ✅ Kept (our code)
    '/opt/render/project/src/voice_model/azrt2021/',  # ✅ Kept (our package)
    # '/opt/render/project/src/' removed ❌
    ...
]
```

## Verification

When you deploy, check the diagnostics output in Render logs. You should see:
```
Python path (filtered to remove 'src' references):
  1. /opt/render/project/src/voice_model/  ✅
  2. /opt/render/project/src/voice_model/azrt2021/  ✅
  # No paths ending with 'src' or 'src/'
```

If you see any paths with `⚠️  (contains 'src')` marker, those are being kept only because they're necessary (like the voice_model directory itself).

## Why This Works

1. **Python won't try to import 'src'**: By removing `/opt/render/project/src/` from the path, Python can't accidentally import it as a module
2. **Our code is still accessible**: We keep `/opt/render/project/src/voice_model/` so all our imports work
3. **Double protection**: Both `run.py` and `api.py` filter paths, so it works even if one runs before the other

## Testing

After deploying, the app should start without "No module named 'src'" errors. The diagnostics will show you exactly which paths are being used.

