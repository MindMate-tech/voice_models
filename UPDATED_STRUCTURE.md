# Updated Structure: Nested Person Directories

## ✅ Code Updated for New Structure!

The conversion script has been updated to handle your new data structure:
```
data/
├── [Person Name 1]/
│   ├── [PersonName1]_0.wav
│   ├── [PersonName1]_5.wav
│   └── [PersonName1]_10.wav
├── [Person Name 2]/
│   ├── [PersonName2]_0.wav
│   └── [PersonName2]_15.wav
└── ...
```

## How It Works

1. **Groups files by person** - Uses the folder name (person name) as the patient identifier
2. **Maintains folder structure** - Output .npy files keep the same structure:
   - `data/John Doe/JohnDoe_0.wav` → `data/mfcc_features/John Doe/JohnDoe_0.npy`
3. **Groups all files per person** - All WAV files from the same person folder are grouped together in the CSV
4. **Generates proper CSV** - Creates CSV with one row per person, with all their audio files listed

## Usage

### Quick Start

```bash
cd voice_model
source venv/bin/activate

# Convert all files in the data directory
python auto_convert_audio.py data
```

Or use the shell script:
```bash
./convert_mp3_to_npy.sh
```

### What Gets Created

```
voice_model/
├── data/                          # Your original WAV files
│   ├── [Person Name 1]/
│   │   └── *.wav
│   └── [Person Name 2]/
│       └── *.wav
├── data/
│   ├── mfcc_features/             # Auto-generated .npy files (same structure)
│   │   ├── [Person Name 1]/
│   │   │   └── *.npy
│   │   └── [Person Name 2]/
│   │       └── *.npy
│   └── csv_files/
│       ├── dataset.csv            # Auto-generated CSV
│       └── task_csvs.txt          # Task configuration
```

## CSV Format

The generated CSV will look like:

```csv
idtype,id,mfcc_npy_files,is_demented_at_recording,person_name
FHS,1234,"['mfcc_features/John Doe/JohnDoe_0.npy', 'mfcc_features/John Doe/JohnDoe_5.npy']",0,John Doe
FHS,5678,"['mfcc_features/Jane Smith/JaneSmith_0.npy']",0,Jane Smith
```

**Key points:**
- Each row represents one person (folder)
- All WAV files from the same person are grouped in `mfcc_npy_files`
- `person_name` column shows the original folder name for reference
- `is_demented_at_recording` defaults to 0 - **you should update this with correct labels**

## Next Steps

1. **Run the conversion:**
   ```bash
   python auto_convert_audio.py data
   ```

2. **Review the CSV file:**
   - Open `data/csv_files/dataset.csv`
   - Update the `is_demented_at_recording` column with correct labels (0 or 1)

3. **Train the model:**
   ```bash
   cd azrt2021
   python train.py -tct ../data/csv_files/task_csvs.txt -ti 0 -m cnn
   ```

## Features

✅ **Automatic person grouping** - Files are automatically grouped by folder name  
✅ **Maintains structure** - Output preserves the folder hierarchy  
✅ **Batch processing** - Converts all files at once  
✅ **Error handling** - Continues even if some files fail  
✅ **CSV generation** - Creates ready-to-use CSV file  

## Notes

- The script uses the folder name as the person identifier
- All files from the same person folder are grouped together
- Relative paths are used in the CSV (from the CSV file location)
- Labels default to 0 - remember to update them!

