#!/usr/bin/env python3
"""
Automated WAV to MFCC .npy converter with CSV generation
Updated for nested structure: data/[Person Name]/[PersonName]_[number].wav

This script automatically:
1. Converts all WAV files in nested directories to MFCC .npy files
2. Groups files by person (folder name)
3. Generates a CSV file with proper format for the model
4. Creates the task_csvs.txt file

Usage:
    python auto_convert_audio.py <input_directory> [--output-dir OUTPUT_DIR] [--csv-output CSV_FILE]
    
Example:
    python auto_convert_audio.py data
    python auto_convert_audio.py data --output-dir data/mfcc_features --csv-output data/csv_files/dataset.csv
"""

import sys
import os
import argparse
import pandas as pd
from pathlib import Path
import numpy as np
from collections import defaultdict

# Import the preprocessing function
# Add current directory to path to import preprocess_audio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from preprocess_audio import audio_to_mfcc, load_audio_file
except ImportError:
    # If import fails, define the functions inline
    import numpy as np
    try:
        import librosa
        HAS_LIBROSA = True
    except ImportError:
        HAS_LIBROSA = False
    
    from azrt2021.mfcc import MFCC_Extractor
    
    def load_audio_file(audio_path, sr=16000):
        """Load audio file."""
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if HAS_LIBROSA:
            audio, _ = librosa.load(audio_path, sr=sr, mono=True)
            return audio
        raise RuntimeError("librosa required. Install: pip install librosa")
    
    def audio_to_mfcc(audio_path, output_path, device='cpu', **mfcc_kwargs):
        """Convert audio to MFCC."""
        audio = load_audio_file(audio_path)
        mfcc_extractor = MFCC_Extractor(
            samplerate=16000, winlen=0.025, winstep=0.01, numcep=13,
            nfilt=26, device=device, **mfcc_kwargs
        )
        audio_batch = audio.reshape(1, -1)
        mfcc_features = mfcc_extractor(audio_batch)[0]
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        np.save(output_path, mfcc_features)

# Audio file extensions to process
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac']


def find_audio_files_by_person(directory):
    """
    Find all audio files grouped by person (folder name).
    
    Returns:
        dict: {person_name: [list of audio file paths]}
    """
    directory = Path(directory)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    # Dictionary to group files by person (folder name)
    person_files = defaultdict(list)
    
    # Find all audio files
    for ext in AUDIO_EXTENSIONS:
        for audio_file in directory.rglob(f'*{ext}'):
            # Get the parent directory name (person name)
            person_name = audio_file.parent.name
            
            # Skip if parent is the root data directory itself
            if person_name == directory.name or person_name == 'data':
                # Try to get the next level up
                if audio_file.parent.parent != directory:
                    person_name = audio_file.parent.parent.name
                else:
                    # If file is directly in data/, use filename as person name
                    person_name = audio_file.stem.split('_')[0]
            
            person_files[person_name].append(audio_file)
    
    # Sort files within each person
    for person in person_files:
        person_files[person] = sorted(person_files[person])
    
    return dict(person_files)


def convert_audio_to_mfcc(audio_path, output_path, device='cpu', overwrite=False):
    """
    Convert a single audio file to MFCC .npy file.
    
    Returns:
        Path to the created .npy file, or None if failed
    """
    audio_path = Path(audio_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Skip if already exists and not overwriting
    if output_path.exists() and not overwrite:
        print(f"⏭️  Skipping {audio_path.name} (already exists: {output_path.name})")
        return str(output_path)
    
    try:
        print(f"🔄 Converting: {audio_path.relative_to(audio_path.parents[2])} -> {output_path.name}")
        audio_to_mfcc(str(audio_path), str(output_path), device=device)
        return str(output_path)
    except Exception as e:
        print(f"❌ Error converting {audio_path.name}: {e}")
        return None


def generate_csv_from_persons(person_data, csv_output, labels=None):
    """
    Generate a CSV file from person-grouped data.
    
    Parameters:
    -----------
    person_data : dict
        Dictionary mapping person names to lists of (audio_path, mfcc_path) tuples
    csv_output : str
        Path to output CSV file
    labels : dict, optional
        Dictionary mapping person names to labels. If None, all labels set to 0.
    """
    csv_output = Path(csv_output)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    
    rows = []
    csv_dir = csv_output.parent
    
    for person_name, files_list in person_data.items():
        # Get all successful MFCC files for this person
        mfcc_files = [mfcc for audio, mfcc in files_list if mfcc is not None]
        
        if not mfcc_files:
            print(f"⚠️  Warning: No valid MFCC files for {person_name}, skipping...")
            continue
        
        # Get label (default to 0 if not provided)
        label = labels.get(person_name, 0) if labels else 0
        
        # Convert to relative paths
        mfcc_rel_paths = []
        for mfcc_file in mfcc_files:
            try:
                mfcc_rel_path = os.path.relpath(mfcc_file, csv_dir)
            except ValueError:
                # If relative path fails, use absolute
                mfcc_rel_path = mfcc_file
            mfcc_rel_paths.append(mfcc_rel_path)
        
        # Format MFCC files as list string
        mfcc_list_str = str(mfcc_rel_paths).replace("'", "'")
        
        # Create a clean ID from person name
        # Remove spaces and special characters, use first part
        person_id = person_name.replace(' ', '_').replace('/', '_').upper()
        # Extract numeric part if exists, otherwise use first 10 chars
        import re
        numbers = re.findall(r'\d+', person_id)
        if numbers:
            person_id_num = numbers[0].zfill(4)
        else:
            # Use hash of name to create unique numeric ID
            person_id_num = str(abs(hash(person_name)) % 10000).zfill(4)
        
        rows.append({
            'idtype': 'FHS',
            'id': person_id_num,
            'mfcc_npy_files': mfcc_list_str,
            'is_demented_at_recording': label,
            'person_name': person_name  # Keep original name for reference
        })
    
    if not rows:
        print(f"\n⚠️  Warning: No successful conversions! CSV file not created.")
        print(f"   All audio file conversions failed. Please check the errors above.")
        return None
    
    df = pd.DataFrame(rows)
    # Reorder columns: person_name last for reference
    cols = ['idtype', 'id', 'mfcc_npy_files', 'is_demented_at_recording', 'person_name']
    df = df[cols]
    df.to_csv(csv_output, index=False)
    
    print(f"\n✅ CSV file created: {csv_output}")
    total_audio_files = sum(len([f for _, f in files if f is not None]) for files in person_data.values())
    print(f"   Found {len(rows)} persons with {total_audio_files} audio files")
    
    return csv_output


def auto_convert_directory(input_dir, output_dir=None, csv_output=None, device='cpu', overwrite=False, labels=None):
    """
    Automatically convert all audio files in a directory and generate CSV.
    Handles nested structure: data/[Person Name]/[PersonName]_[number].wav
    
    Parameters:
    -----------
    input_dir : str
        Directory containing audio files (e.g., 'data' with subdirectories)
    output_dir : str, optional
        Directory to save .npy files (default: input_dir/../mfcc_features)
    csv_output : str, optional
        Path to output CSV file (default: input_dir/../csv_files/dataset.csv)
    device : str
        Device to use for processing
    overwrite : bool
        Whether to overwrite existing .npy files
    labels : dict, optional
        Dictionary mapping person names to labels
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    # Set default output directory
    if output_dir is None:
        # If input is 'data', output to 'data/mfcc_features'
        # Otherwise, output to parent/mfcc_features
        if input_dir.name == 'data':
            output_dir = input_dir.parent / 'data' / 'mfcc_features'
        else:
            output_dir = input_dir.parent / 'mfcc_features'
    else:
        output_dir = Path(output_dir)
    
    # Set default CSV output
    if csv_output is None:
        if input_dir.name == 'data':
            csv_output = input_dir.parent / 'data' / 'csv_files' / 'dataset.csv'
        else:
            csv_output = input_dir.parent / 'csv_files' / 'dataset.csv'
    else:
        csv_output = Path(csv_output)
    
    print(f"📁 Input directory: {input_dir}")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 CSV output: {csv_output}")
    print()
    
    # Find all audio files grouped by person
    print("🔍 Searching for audio files grouped by person...")
    person_files = find_audio_files_by_person(input_dir)
    
    if not person_files:
        print(f"❌ No audio files found in {input_dir}")
        print(f"   Supported formats: {', '.join(AUDIO_EXTENSIONS)}")
        return None, None
    
    total_files = sum(len(files) for files in person_files.values())
    print(f"✅ Found {len(person_files)} person(s) with {total_files} audio file(s)")
    print()
    
    # Convert all audio files, maintaining folder structure
    print("🔄 Converting audio files to MFCC features...")
    person_data = {}
    
    for person_name, audio_files in person_files.items():
        print(f"\n👤 Processing: {person_name} ({len(audio_files)} files)")
        person_mfcc_files = []
        
        for i, audio_file in enumerate(audio_files, 1):
            # Maintain folder structure in output
            # e.g., data/Person Name/file.wav -> mfcc_features/Person Name/file.npy
            relative_path = audio_file.relative_to(input_dir)
            output_file = output_dir / relative_path.with_suffix('.npy')
            
            print(f"  [{i}/{len(audio_files)}] ", end='')
            mfcc_file = convert_audio_to_mfcc(audio_file, output_file, device=device, overwrite=overwrite)
            person_mfcc_files.append((audio_file, mfcc_file))
        
        person_data[person_name] = person_mfcc_files
    
    # Count successful conversions
    successful = sum(1 for files in person_data.values() for _, mfcc in files if mfcc is not None)
    print(f"\n✅ Successfully converted {successful}/{total_files} files")
    print()
    
    # Generate CSV file
    print("📝 Generating CSV file...")
    csv_path = generate_csv_from_persons(person_data, csv_output, labels=labels)
    
    if csv_path is None:
        print("\n❌ Cannot create task file - no CSV was generated (all conversions failed)")
        return None, None
    
    # Create task_csvs.txt in the CSV directory
    task_file = csv_output.parent / 'task_csvs.txt'
    csv_rel_path = os.path.relpath(csv_output, task_file.parent)
    with open(task_file, 'w') as f:
        f.write(f"{csv_rel_path}, norm_vs_ad\n")
    print(f"✅ Task file created: {task_file}")
    
    # Also create task_csvs.txt in the root csv_files directory for easy access from azrt2021/
    # This matches the expected path: ../csv_files/task_csvs.txt when running from azrt2021/
    root_csv_dir = input_dir.parent / 'csv_files'
    root_csv_dir.mkdir(exist_ok=True)
    root_task_file = root_csv_dir / 'task_csvs.txt'
    # Calculate path from root csv_files to the actual CSV file
    csv_rel_from_root = os.path.relpath(csv_output, root_csv_dir)
    with open(root_task_file, 'w') as f:
        f.write(f"{csv_rel_from_root}, norm_vs_ad\n")
    print(f"✅ Task file also created at: {root_task_file} (for running from azrt2021/)")
    
    print("\n" + "="*60)
    print("🎉 Conversion complete!")
    print("="*60)
    print(f"\nNext steps:")
    print(f"1. Review the CSV file: {csv_output}")
    print(f"2. Update labels if needed (column: is_demented_at_recording)")
    print(f"3. Train the model:")
    print(f"   cd azrt2021")
    print(f"   python train.py -tct ../{task_file.relative_to(csv_output.parent.parent)} -ti 0 -m cnn")
    
    return csv_path, task_file


def main():
    parser = argparse.ArgumentParser(
        description='Automatically convert WAV files to MFCC .npy files and generate CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - convert all audio files in data directory
  python auto_convert_audio.py data
  
  # Specify output directories
  python auto_convert_audio.py data --output-dir data/mfcc_features --csv-output data/csv_files/my_dataset.csv
  
  # Overwrite existing files
  python auto_convert_audio.py data --overwrite
        """
    )
    parser.add_argument('input_dir', help='Directory containing audio files (e.g., "data" with person subdirectories)')
    parser.add_argument('--output-dir', help='Directory to save .npy files (default: data/mfcc_features)')
    parser.add_argument('--csv-output', help='Path to output CSV file (default: data/csv_files/dataset.csv)')
    parser.add_argument('--device', default='cpu', help='Device to use: "cpu" or GPU index (default: cpu)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing .npy files')
    
    args = parser.parse_args()
    
    try:
        auto_convert_directory(
            args.input_dir,
            output_dir=args.output_dir,
            csv_output=args.csv_output,
            device=args.device,
            overwrite=args.overwrite
        )
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
