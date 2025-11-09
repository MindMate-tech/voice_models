# 🎉 Automatic MP3 to .npy Conversion - READY TO USE!

## Answer: YES, Automatic Conversion is Available!

**You do NOT need to convert MP3 files manually.** The system does it automatically for you!

## 🚀 Super Simple Usage

### Step 1: Place Your MP3 Files
```bash
mkdir -p voice_model/data/audio_raw
# Copy your MP3/WAV files here
cp your_audio_files/*.mp3 voice_model/data/audio_raw/
```

### Step 2: Run Automatic Conversion
```bash
cd voice_model
./convert_mp3_to_npy.sh
```

**That's it!** The script will:
- ✅ Convert all MP3/WAV files to .npy files automatically
- ✅ Generate the CSV file automatically  
- ✅ Create the task configuration file automatically
- ✅ Everything is ready for training!

### Step 3: Review CSV (Optional)
Edit `data/csv_files/dataset.csv` to update labels if needed.

### Step 4: Train Model
```bash
cd azrt2021
python train.py -tct ../data/csv_files/task_csvs.txt -ti 0 -m cnn
```

## 📋 What You Get

After running the conversion script:

```
voice_model/
├── data/
│   ├── audio_raw/          ← You place MP3 files here
│   ├── mfcc_features/       ← Auto-generated .npy files
│   └── csv_files/          ← Auto-generated CSV files
│       ├── dataset.csv
│       └── task_csvs.txt
```

## 🔧 Alternative: Python Script

If you prefer using Python directly:

```bash
cd voice_model
source venv/bin/activate
python auto_convert_audio.py data/audio_raw
```

## 📚 More Information

- **Quick Start Guide**: See `QUICK_START.md`
- **Detailed Guide**: See `AUTOMATIC_CONVERSION.md`
- **Full Documentation**: See `AUDIO_SETUP_GUIDE.md`

## ✨ Features

- ✅ **Fully Automatic** - No manual conversion needed
- ✅ **Batch Processing** - Converts all files at once
- ✅ **CSV Generation** - Creates metadata file automatically
- ✅ **Multiple Formats** - Supports MP3, WAV, FLAC, M4A, OGG, AAC
- ✅ **Smart Naming** - Extracts patient IDs from filenames
- ✅ **Error Handling** - Skips failed files and continues

## 🎯 Summary

**Question:** Do I need to convert MP3 files manually?  
**Answer:** **NO!** Just run `./convert_mp3_to_npy.sh` and everything is done automatically! 🎉

