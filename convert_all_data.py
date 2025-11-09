#!/usr/bin/env python3
"""
Convert audio files from both dementia and normal (nodementia) folders to MFCC .npy files
and generate a combined CSV with correct labels.

This script:
1. Processes data/ folder (dementia cases) -> label = 1
2. Processes nodementia/ folder (normal cases) -> label = 0
3. Converts all WAV files to MFCC .npy files
4. Generates a combined CSV file with proper labels
5. Creates the task_csvs.txt file

Usage:
    python convert_all_data.py [--dementia-dir DEMENTIA_DIR] [--normal-dir NORMAL_DIR] [--output-dir OUTPUT_DIR] [--csv-output CSV_FILE]
    
Example:
    python convert_all_data.py
    python convert_all_data.py --dementia-dir data --normal-dir nodementia --output-dir data/mfcc_features --csv-output data/csv_files/dataset.csv
"""

import sys
import os
import argparse
import pandas as pd
from pathlib import Path
import numpy as np
from collections import defaultdict

# Import the preprocessing function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from preprocess_audio import audio_to_mfcc, load_audio_file
except ImportError:
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
    
    return person_files


def convert_audio_to_mfcc(audio_path, output_dir, person_name, device='cpu'):
    """
    Convert a single audio file to MFCC .npy format.
    
    Returns:
        Path to the created .npy file, or None if conversion failed
    """
    try:
        # Create output path: output_dir/person_name/filename.npy
        audio_path = Path(audio_path)
        output_dir = Path(output_dir)
        person_dir = output_dir / person_name
        person_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output filename
        output_file = person_dir / f"{audio_path.stem}.npy"
        
        # Convert to MFCC
        audio_to_mfcc(str(audio_path), str(output_file), device=device)
        
        return output_file
    except Exception as e:
        print(f"   ❌ Error converting {audio_path}: {e}")
        return None


def generate_csv_from_persons(person_data, csv_output, label, labels_dict=None):
    """
    Generate CSV file from person data.
    
    Parameters:
    -----------
    person_data : dict
        {person_name: [(audio_path, mfcc_path), ...]}
    csv_output : Path
        Output CSV file path
    label : int
        Default label for all persons (0 for normal, 1 for dementia)
    labels_dict : dict, optional
        {person_name: label} to override default label per person
    """
    rows = []
    csv_dir = csv_output.parent
    
    for person_name, files_list in person_data.items():
        mfcc_files = [mfcc for audio, mfcc in files_list if mfcc is not None]
        
        if not mfcc_files:
            print(f"⚠️  Warning: No valid MFCC files for {person_name}, skipping...")
            continue
        
        # Use label from labels_dict if provided, otherwise use default
        person_label = labels_dict.get(person_name, label) if labels_dict else label
        
        mfcc_rel_paths = []
        for mfcc_file in mfcc_files:
            try:
                mfcc_rel_path = os.path.relpath(mfcc_file, csv_dir)
            except ValueError:
                mfcc_rel_path = mfcc_file
            mfcc_rel_paths.append(mfcc_rel_path)
        
        mfcc_list_str = str(mfcc_rel_paths).replace("'", "'")
        
        # Generate person ID
        person_id = person_name.replace(' ', '_').replace('/', '_').upper()
        import re
        numbers = re.findall(r'\d+', person_id)
        if numbers:
            person_id_num = numbers[0].zfill(4)
        else:
            person_id_num = str(abs(hash(person_name)) % 10000).zfill(4)
        
        rows.append({
            'idtype': 'FHS',
            'id': person_id_num,
            'mfcc_npy_files': mfcc_list_str,
            'is_demented_at_recording': person_label,
            'person_name': person_name
        })
    
    if not rows:
        print(f"\n⚠️  Warning: No successful conversions! CSV file not created.")
        print(f"   All audio file conversions failed. Please check the errors above.")
        return None
    
    df = pd.DataFrame(rows)
    cols = ['idtype', 'id', 'mfcc_npy_files', 'is_demented_at_recording', 'person_name']
    df = df[cols]
    df.to_csv(csv_output, index=False)
    
    print(f"\n✅ CSV file created: {csv_output}")
    total_audio_files = sum(len([f for _, f in files if f is not None]) for files in person_data.values())
    print(f"   Found {len(rows)} persons with {total_audio_files} audio files")
    
    return csv_output


def process_directory(input_dir, output_dir, label, device='cpu'):
    """
    Process a directory of audio files and convert them to MFCC.
    
    Parameters:
    -----------
    input_dir : str or Path
        Input directory containing person subdirectories
    output_dir : str or Path
        Output directory for MFCC files
    label : int
        Label for all persons in this directory (0 for normal, 1 for dementia)
    device : str
        Device to use for processing ('cpu' or 'cuda:0')
    
    Returns:
    --------
    dict: {person_name: [(audio_path, mfcc_path), ...]}
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    
    print(f"\n{'='*60}")
    print(f"Processing: {input_dir}")
    print(f"Label: {label} ({'Normal' if label == 0 else 'Dementia'})")
    print(f"{'='*60}")
    
    # Find all audio files grouped by person
    person_files = find_audio_files_by_person(input_dir)
    
    if not person_files:
        print(f"⚠️  No audio files found in {input_dir}")
        return {}
    
    print(f"Found {len(person_files)} persons with audio files")
    
    # Convert all audio files to MFCC
    person_data = defaultdict(list)
    total_files = sum(len(files) for files in person_files.values())
    processed = 0
    
    for person_name, audio_files in person_files.items():
        print(f"\n[{processed+1}/{total_files}] Processing {person_name} ({len(audio_files)} files)...")
        
        for audio_file in sorted(audio_files):
            processed += 1
            print(f"   Converting: {audio_file.name}...", end=' ', flush=True)
            
            mfcc_file = convert_audio_to_mfcc(audio_file, output_dir, person_name, device=device)
            person_data[person_name].append((audio_file, mfcc_file))
            
            if mfcc_file:
                print("✅")
            else:
                print("❌")
    
    return person_data


def create_task_file(csv_output, task_file_path):
    """Create task_csvs.txt file pointing to the CSV."""
    task_file_path = Path(task_file_path)
    task_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get relative path from task file to CSV
    csv_path = Path(csv_output)
    try:
        rel_path = os.path.relpath(csv_path, task_file_path.parent)
    except ValueError:
        rel_path = str(csv_path)
    
    # Format: csv_path,extension (both on same line, comma-separated)
    with open(task_file_path, 'w') as f:
        f.write(f"{rel_path},norm_vs_ad\n")
    
    print(f"✅ Task file created: {task_file_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert audio files from both dementia and normal folders to MFCC and generate CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--dementia-dir', default='data',
                       help='Directory containing dementia cases (default: data)')
    parser.add_argument('--normal-dir', default='nodementia',
                       help='Directory containing normal cases (default: nodementia)')
    parser.add_argument('--output-dir', default='data/mfcc_features',
                       help='Output directory for MFCC .npy files (default: data/mfcc_features)')
    parser.add_argument('--csv-output', default='data/csv_files/dataset.csv',
                       help='Output CSV file path (default: data/csv_files/dataset.csv)')
    parser.add_argument('--device', default='cpu',
                       help='Device to use: "cpu" or "cuda:0" (default: cpu)')
    parser.add_argument('--skip-conversion', action='store_true',
                       help='Skip audio conversion (use existing MFCC files)')
    
    args = parser.parse_args()
    
    # Convert paths to Path objects
    dementia_dir = Path(args.dementia_dir)
    normal_dir = Path(args.normal_dir)
    output_dir = Path(args.output_dir)
    csv_output = Path(args.csv_output)
    
    # Check if directories exist
    if not dementia_dir.exists():
        print(f"❌ Error: Dementia directory not found: {dementia_dir}")
        sys.exit(1)
    
    if not normal_dir.exists():
        print(f"❌ Error: Normal directory not found: {normal_dir}")
        sys.exit(1)
    
    print("="*60)
    print("Voice Model - Combined Data Conversion")
    print("="*60)
    print(f"Dementia directory: {dementia_dir}")
    print(f"Normal directory: {normal_dir}")
    print(f"Output directory: {output_dir}")
    print(f"CSV output: {csv_output}")
    print("="*60)
    
    # Process dementia cases (label = 1)
    if args.skip_conversion:
        print("\n⚠️  Skipping audio conversion (using existing MFCC files)")
        # Load existing person data structure
        dementia_data = find_audio_files_by_person(dementia_dir)
        # Convert to expected format (would need to find existing .npy files)
        print("   Note: Skip conversion mode requires existing MFCC files")
    else:
        dementia_data = process_directory(dementia_dir, output_dir, label=1, device=args.device)
    
    # Process normal cases (label = 0)
    if args.skip_conversion:
        normal_data = find_audio_files_by_person(normal_dir)
        print("   Note: Skip conversion mode requires existing MFCC files")
    else:
        normal_data = process_directory(normal_dir, output_dir, label=0, device=args.device)
    
    # Combine both datasets
    print(f"\n{'='*60}")
    print("Combining datasets...")
    print(f"{'='*60}")
    
    all_person_data = {}
    all_person_data.update(dementia_data)
    
    # Check for name conflicts
    conflicts = set(dementia_data.keys()) & set(normal_data.keys())
    if conflicts:
        print(f"⚠️  Warning: Found {len(conflicts)} name conflicts between dementia and normal data:")
        for name in conflicts:
            print(f"   - {name}")
        print("   Adding suffix to normal cases...")
        for name in conflicts:
            normal_data[f"{name}_normal"] = normal_data.pop(name)
    
    all_person_data.update(normal_data)
    
    # Create labels dictionary
    labels_dict = {}
    for name in dementia_data.keys():
        labels_dict[name] = 1  # Dementia
    for name in normal_data.keys():
        labels_dict[name] = 0  # Normal
    
    # Generate combined CSV
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    generate_csv_from_persons(all_person_data, csv_output, label=0, labels_dict=labels_dict)
    
    # Create task file
    task_file1 = csv_output.parent / 'task_csvs.txt'
    task_file2 = Path('csv_files') / 'task_csvs.txt'
    
    create_task_file(csv_output, task_file1)
    create_task_file(csv_output, task_file2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    dementia_count = len(dementia_data)
    normal_count = len(normal_data)
    total_persons = len(all_person_data)
    total_files = sum(len(files) for files in all_person_data.values())
    
    print(f"Dementia cases: {dementia_count} persons")
    print(f"Normal cases: {normal_count} persons")
    print(f"Total: {total_persons} persons, {total_files} audio files")
    print(f"\n✅ CSV file: {csv_output}")
    print(f"✅ Ready for training!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()

