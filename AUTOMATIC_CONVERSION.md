# Automatic MP3 to .npy Conversion

## ✅ Yes! Automatic Conversion is Available

The system **automatically converts MP3 files to .npy files** for you. You don't need to do it manually!

## Quick Start (Easiest Method)

### Option 1: Use the Shell Script (Simplest)

```bash
cd voice_model
./convert_mp3_to_npy.sh
```

This will:
1. Create `data/audio_raw/` directory if it doesn't exist
2. Ask you to place MP3 files there
3. Automatically convert all MP3/WAV files to .npy files
4. Generate the CSV file automatically
5. Create the task configuration file

### Option 2: Use Python Script Directly

```bash
cd voice_model
source venv/bin/activate

# Place your MP3 files in a directory (e.g., data/audio_raw)
python auto_convert_audio.py data/audio_raw
```

## How It Works

1. **Place your MP3/WAV files** in a directory (e.g., `data/audio_raw/`)
2. **Run the conversion script** - it will:
   - Find all audio files (MP3, WAV, FLAC, M4A, OGG, AAC)
   - Convert each to MFCC .npy files
   - Save .npy files to `data/mfcc_features/`
   - Generate a CSV file with all the metadata
   - Create `task_csvs.txt` for training

3. **Review and edit the CSV** if needed (update labels)
4. **Train the model** - everything is ready!

## Example Workflow

```bash
# 1. Create directory and place MP3 files
mkdir -p voice_model/data/audio_raw
cp your_audio_files/*.mp3 voice_model/data/audio_raw/

# 2. Run automatic conversion
cd voice_model
./convert_mp3_to_npy.sh

# 3. The script will:
#    - Convert all MP3 files to .npy
#    - Create data/csv_files/dataset.csv
#    - Create data/csv_files/task_csvs.txt

# 4. Review the CSV file (update labels if needed)
#    Edit: data/csv_files/dataset.csv

# 5. Train the model
cd azrt2021
python train.py -tct ../data/csv_files/task_csvs.txt -ti 0 -m cnn
```

## Advanced Options

### Custom Output Directories

```bash
python auto_convert_audio.py data/audio_raw \
    --output-dir data/my_mfcc_files \
    --csv-output data/my_csv_files/my_dataset.csv
```

### Overwrite Existing Files

```bash
python auto_convert_audio.py data/audio_raw --overwrite
```

### Use GPU (if available)

```bash
python auto_convert_audio.py data/audio_raw --device 0
```

## What Gets Created

After running the conversion:

```
voice_model/
├── data/
│   ├── audio_raw/              # Your original MP3 files (you place these)
│   ├── mfcc_features/          # Auto-generated .npy files
│   │   ├── audio1.npy
│   │   ├── audio2.npy
│   │   └── ...
│   └── csv_files/              # Auto-generated CSV files
│       ├── dataset.csv         # Main dataset file
│       └── task_csvs.txt       # Task configuration
```

## CSV File Format

The script automatically generates a CSV like this:

```csv
idtype,id,mfcc_npy_files,is_demented_at_recording
FHS,0001,"['mfcc_features/audio1.npy']",0
FHS,0002,"['mfcc_features/audio2.npy']",0
```

**Important:** You should review and update the `is_demented_at_recording` column with the correct labels (0 or 1) for each patient.

## Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)
- M4A (`.m4a`)
- OGG (`.ogg`)
- AAC (`.aac`)

## Troubleshooting

### "No audio files found"
- Make sure your files are in the input directory
- Check that file extensions are supported (see above)
- Files are searched recursively in subdirectories

### "librosa not found"
```bash
source venv/bin/activate
pip install librosa soundfile
```

### "Permission denied"
```bash
chmod +x convert_mp3_to_npy.sh
chmod +x auto_convert_audio.py
```

## Summary

✅ **Automatic conversion is built-in!**  
✅ **Just place MP3 files and run the script**  
✅ **CSV file is generated automatically**  
✅ **Everything is ready for training**

No manual conversion needed! 🎉

