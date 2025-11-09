# Quick Start: Where to Place MP3 Files

## TL;DR - The Answer

**MP3 files should NOT be placed directly in the model directory.** Instead:

1. **Convert MP3 files to MFCC .npy files** using the preprocessing script
2. **Place the .npy files** in a directory (e.g., `data/mfcc_features/`)
3. **Reference the .npy file paths** in your CSV metadata file

## Step-by-Step Workflow

### 1. Create Directory Structure
```bash
cd voice_model
mkdir -p data/audio_raw      # Optional: store original MP3 files here
mkdir -p data/mfcc_features  # Store converted .npy files here
mkdir -p data/csv_files      # Store your CSV metadata files here
```

### 2. Convert MP3 to MFCC Features

**Single file:**
```bash
source venv/bin/activate
python preprocess_audio.py path/to/your/audio.mp3 data/mfcc_features/audio1.npy
```

**Batch processing (all files in a directory):**
```bash
python preprocess_audio.py --batch data/audio_raw data/mfcc_features
```

### 3. Create CSV File

Create a CSV file (e.g., `data/csv_files/my_dataset.csv`) with this format:

```csv
idtype,id,mfcc_npy_files,is_demented_at_recording
FHS,0001,"['data/mfcc_features/audio1.npy']",0
FHS,0002,"['data/mfcc_features/audio2.npy']",1
```

**Important:** The `mfcc_npy_files` column should contain paths to the `.npy` files (not MP3 files), formatted as a Python list string.

### 4. Create Task File

Create `task_csvs.txt`:
```
data/csv_files/my_dataset.csv, norm_vs_ad
```

### 5. Train the Model

```bash
cd azrt2021
python train.py -tct ../task_csvs.txt -ti 0 -m cnn
```

## File Paths in CSV

- **Absolute paths:** `/full/path/to/file.npy`
- **Relative paths:** `data/mfcc_features/file.npy` (relative to where you run `train.py`)
- **Multiple files per patient:** `['file1.npy', 'file2.npy', 'file3.npy']`

## Example Directory Structure

```
voice_model/
├── data/
│   ├── audio_raw/              # Your original MP3 files (optional)
│   │   ├── patient_001.mp3
│   │   └── patient_002.mp3
│   ├── mfcc_features/          # Converted .npy files (REQUIRED)
│   │   ├── patient_001.npy
│   │   └── patient_002.npy
│   └── csv_files/              # Your CSV metadata files
│       └── my_dataset.csv
├── azrt2021/                   # Model code
├── preprocess_audio.py         # Conversion script
└── task_csvs.txt              # Task configuration
```

## Why Not Direct MP3?

The model is designed to work with pre-extracted MFCC features for efficiency. The model loads features directly:
```python
fea = np.load(audio_fn)  # Loads .npy file, not MP3
```

This avoids re-computing MFCC features every time during training/testing.

