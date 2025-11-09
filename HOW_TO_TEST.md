# How to Test Your Trained Model on a Voice

## Quick Start

### 1. Test a Single Audio File

```bash
cd voice_model
source venv/bin/activate

# Test with auto-detected model (uses most recent trained model)
python test_voice.py path/to/your/audio.wav

# Or specify a specific model
python test_voice.py path/to/your/audio.mp3 azrt2021/pt_files/cnn_norm_vs_ad_github_test_with_loss_weights_1.0_1.0/cnn_norm_vs_ad_github_test_with_loss_weights_1.0_1.0_0_72901_1_2025-11-08_17:06:14.833328_epochs.pt
```

### 2. Supported Audio Formats

The script supports:
- `.wav` (recommended)
- `.mp3`
- `.flac`
- `.m4a`
- `.ogg`
- `.aac`

### 3. What the Output Means

The script will display:
- **Normal (Healthy) Probability**: Likelihood the voice is normal (0-100%)
- **Dementia Probability**: Likelihood the voice shows signs of dementia (0-100%)

**Interpretation:**
- If dementia probability > 50%: Possible signs of dementia detected
- If dementia probability < 50%: Voice appears normal

**Important:** This is a screening tool and should not replace professional medical diagnosis.

## Example Usage

```bash
# Test a WAV file
python test_voice.py test_voice.wav

# Test an MP3 file with specific model
python test_voice.py recording.mp3 azrt2021/pt_files/.../model.pt

# Use CPU explicitly (default on MacBook)
python test_voice.py test_voice.wav --device cpu
```

## Finding Your Trained Models

Trained models are saved in:
- `azrt2021/pt_files/` - Final trained models
- `azrt2021/results/.../tmp.pt` - Best model from each training run

The script automatically uses the most recent model if you don't specify one.

## Troubleshooting

### "Audio file not found"
- Make sure the path to your audio file is correct
- Use absolute paths if relative paths don't work

### "No trained model found"
- Make sure you've trained a model first using `python azrt2021/train.py`
- Or specify the model path explicitly

### "librosa not found"
- Install librosa: `pip install librosa soundfile`

## Advanced: Batch Testing

If you want to test multiple files, you can create a simple loop:

```bash
for file in audio_files/*.wav; do
    python test_voice.py "$file"
    echo "---"
done
```

