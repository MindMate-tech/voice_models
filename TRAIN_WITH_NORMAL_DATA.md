# Training with Both Dementia and Normal Data

## Overview

This guide shows you how to train the model using both:
- **Dementia cases** from the `data/` folder (label = 1)
- **Normal cases** from the `nodementia/` folder (label = 0)

## Quick Start

### Step 1: Convert Audio Files to MFCC

Run the conversion script to process both folders:

```bash
cd voice_model
source venv/bin/activate

# Convert all audio files and generate combined CSV
python convert_all_data.py
```

This will:
1. Process `data/` folder (dementia cases) → label = 1
2. Process `nodementia/` folder (normal cases) → label = 0
3. Convert all WAV files to MFCC .npy files
4. Generate a combined CSV at `data/csv_files/dataset.csv`
5. Create `task_csvs.txt` files

### Step 2: Train the Model

Once conversion is complete, train the model:

```bash
cd azrt2021
python train.py -ti 0 -m cnn
```

## Script Options

### Basic Usage
```bash
python convert_all_data.py
```

### Custom Directories
```bash
python convert_all_data.py \
    --dementia-dir data \
    --normal-dir nodementia \
    --output-dir data/mfcc_features \
    --csv-output data/csv_files/dataset.csv
```

### Skip Conversion (Use Existing MFCC Files)
```bash
python convert_all_data.py --skip-conversion
```

### Use GPU (if available)
```bash
python convert_all_data.py --device cuda:0
```

## What Gets Created

1. **MFCC Files**: `data/mfcc_features/[Person Name]/[filename].npy`
   - All audio files converted to MFCC features
   - Organized by person name

2. **CSV File**: `data/csv_files/dataset.csv`
   - Contains all persons from both folders
   - Labels: `is_demented_at_recording`
     - `0` = Normal (from nodementia folder)
     - `1` = Dementia (from data folder)

3. **Task File**: `data/csv_files/task_csvs.txt`
   - Points to the dataset CSV
   - Used by training script

## Label Mapping

| Folder | Label | Meaning |
|--------|-------|---------|
| `data/` | 1 | Dementia cases |
| `nodementia/` | 0 | Normal/healthy cases |

## Verification

After conversion, check the CSV:

```bash
# Check label distribution
python3 << 'EOF'
import pandas as pd
df = pd.read_csv('data/csv_files/dataset.csv')
print("Label distribution:")
print(df['is_demented_at_recording'].value_counts())
print(f"\nTotal persons: {len(df)}")
print(f"Dementia cases: {len(df[df['is_demented_at_recording']==1])}")
print(f"Normal cases: {len(df[df['is_demented_at_recording']==0])}")
EOF
```

## Troubleshooting

### "Directory not found"
- Make sure `data/` and `nodementia/` folders exist
- Check you're running from the `voice_model/` directory

### "No audio files found"
- Check that WAV files are in subdirectories (e.g., `data/Person Name/file.wav`)
- Supported formats: `.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`, `.aac`

### Name Conflicts
- If a person name appears in both folders, the script will add `_normal` suffix to the normal case

### Conversion Errors
- Check that `librosa` and `soundfile` are installed: `pip install librosa soundfile`
- Verify audio files are not corrupted

## Next Steps

After successful conversion and training:
1. Test the model: `python test_voice.py <audio_file>`
2. Check training results in `azrt2021/results/`
3. Find trained models in `azrt2021/pt_files/`

