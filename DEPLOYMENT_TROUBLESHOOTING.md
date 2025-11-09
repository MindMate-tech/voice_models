# Render Deployment Troubleshooting

## Build Successful but Deployment Fails

If your build succeeds but deployment fails, here are the most common causes:

### 1. **Module Import Errors** (Most Common)
**Symptom**: `ModuleNotFoundError: No module named 'src'` or `ModuleNotFoundError: No module named 'api'`

**Solution**: 
- Use `run.py` startup script (already implemented)
- Ensure `rootDir: voice_model` is set in `render.yaml`
- Check that all Python files are committed to Git

### 2. **Missing Model Files**
**Symptom**: App starts but model loading fails

**Solution**:
- Model files are large and may not be in Git
- Set `MODEL_URL` environment variable in Render dashboard
- Or ensure model files are in `azrt2021/pt_files/` directory

### 3. **Python Version Mismatch**
**Symptom**: Import errors or compatibility issues

**Solution**:
- Check `runtime.txt` specifies correct version (3.11.0)
- Ensure `PYTHON_VERSION` env var matches in `render.yaml`

### 4. **Working Directory Issues**
**Symptom**: File not found errors

**Solution**:
- `run.py` now changes to script directory with `os.chdir()`
- This ensures all relative paths work correctly

### 5. **Missing Runtime Dependencies**
**Symptom**: Import errors for specific packages

**Solution**:
- Check `requirements.txt` includes all dependencies
- Some packages might need system libraries (e.g., librosa needs ffmpeg)

## Debugging Steps

1. **Check Render Logs**:
   - Go to Render dashboard → Your service → Logs
   - Look for the exact error message
   - Check the debug output from `run.py`

2. **Verify File Structure**:
   - Ensure `api.py`, `run.py`, `requirements.txt` are in `voice_model/` directory
   - Check that `azrt2021/` directory exists with `__init__.py`

3. **Test Locally**:
   ```bash
   cd voice_model
   python run.py
   ```
   If this works locally but fails on Render, it's an environment issue.

4. **Check Environment Variables**:
   - `PORT` is set automatically by Render
   - `MODEL_URL` should be set if using external model storage
   - `PYTHON_VERSION` should match `runtime.txt`

## Quick Fixes

### If still getting "No module named 'src'":
1. Verify `rootDir: voice_model` in `render.yaml`
2. Check that `run.py` is in the `voice_model/` directory
3. Ensure start command is `python run.py`

### If model loading fails:
1. Set `MODEL_URL` environment variable in Render
2. Or ensure model files are committed to Git (if small enough)
3. The app will still start - model loads on first request

### If imports fail:
1. Check `requirements.txt` has all packages
2. Verify Python version matches
3. Check Render logs for specific missing module

