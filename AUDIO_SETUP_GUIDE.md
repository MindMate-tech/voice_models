# Audio File Setup Guide

## Important: The Model Uses MFCC Features, Not Raw Audio

This model expects **MFCC numpy files (.npy)**, not raw MP3/WAV files. You need to preprocess your audio files first.

## Directory Structure

Recommended structure:
```
voice_model/
├── data/
│   ├── audio_raw/          # Place your MP3/WAV files here (optional)
│   ├── mfcc_features/      # Place converted .npy MFCC files here
│   └── csv_files/          # Place your CSV metadata files here
├── azrt2021/               # Model code
└── venv/                   # Virtual environment
```

## Step 1: Convert Audio Files to MFCC Features

The model expects MFCC (Mel-frequency cepstral coefficients) features saved as `.npy` files. 

### Option A: Use the provided preprocessing script

See `preprocess_audio.py` (created below) to convert your MP3/WAV files to MFCC .npy files.

### Option B: Manual conversion

1. Load your audio file (MP3/WAV) using librosa or soundfile
2. Extract MFCC features using the `MFCC_Extractor` class from `mfcc.py`
3. Save the features as a `.npy` file

## Step 2: Create CSV Metadata File

Your CSV file should contain the following columns:

### Required Columns:
- `idtype`: Patient ID type (e.g., "FHS")
- `id`: Patient ID number (will be zero-padded to 4 digits)
- `mfcc_npy_files`: Paths to MFCC .npy files (as a list format: `['path/to/file1.npy', 'path/to/file2.npy']`)
- Label column (one of):
  - `is_demented_at_recording`: 1 for demented, 0 for not
  - `is_ad`: 1 for Alzheimer's, 0 for not
  - `is_mci`: 1 for MCI, 0 for not

### Optional Columns:
- `duration_csv_out_list`: Paths to transcript CSV files (same format as mfcc_npy_files)
- `has_transcript_and_nearby_mri`: "1" if transcript and MRI available

### Example CSV Format:

```csv
idtype,id,mfcc_npy_files,is_demented_at_recording
FHS,0001,"['data/mfcc_features/patient_001_audio1.npy', 'data/mfcc_features/patient_001_audio2.npy']",0
FHS,0002,"['data/mfcc_features/patient_002_audio1.npy']",1
```

### File Paths in CSV

- Paths can be **absolute** (e.g., `/full/path/to/file.npy`)
- Paths can be **relative** (e.g., `data/mfcc_features/file.npy`) - relative to where you run the training script
- Multiple files per patient should be in list format: `['file1.npy', 'file2.npy']`

## Step 3: Create Task CSV Text File

Create a text file (e.g., `task_csvs.txt`) that lists your CSV files:

```
data/csv_files/my_dataset.csv, norm_vs_ad
data/csv_files/another_dataset.csv, norm_vs_mci
```

Format: `path_to_csv, task_extension`

## Step 4: Run Training

```bash
cd voice_model
source venv/bin/activate
cd azrt2021
python train.py -tct ../task_csvs.txt -ti 0 -m cnn
```

## Notes

- The model loads MFCC features directly: `fea = np.load(audio_fn)`
- MFCC features should be extracted with:
  - Sample rate: 16000 Hz (default)
  - Window length: 0.025s (25ms)
  - Window step: 0.01s (10ms)
  - Number of cepstral coefficients: 13
- Each .npy file should contain a 2D array: `(num_windows, 13)` where num_windows depends on audio length

