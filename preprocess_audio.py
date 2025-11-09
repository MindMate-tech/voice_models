#!/usr/bin/env python3
"""
Preprocess audio files (MP3/WAV) to MFCC numpy files (.npy)

This script converts raw audio files to MFCC features that the model expects.

Usage:
    python preprocess_audio.py <input_audio_file> <output_npy_file>
    python preprocess_audio.py --batch <input_directory> <output_directory>
"""

import sys
import os
import argparse
import numpy as np

# Try to import audio libraries
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    print("Warning: librosa not found. Install with: pip install librosa")

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

from azrt2021.mfcc import MFCC_Extractor


def load_audio_file(audio_path, sr=16000):
    """
    Load audio file and return audio array.
    
    Parameters:
    -----------
    audio_path : str
        Path to audio file (MP3, WAV, etc.)
    sr : int
        Sample rate (default: 16000 Hz)
    
    Returns:
    --------
    audio : numpy.ndarray
        Audio signal as 1D array
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Try librosa first (supports many formats)
    if HAS_LIBROSA:
        try:
            audio, _ = librosa.load(audio_path, sr=sr, mono=True)
            return audio
        except Exception as e:
            print(f"librosa failed: {e}")
    
    # Fallback to soundfile
    if HAS_SOUNDFILE:
        try:
            audio, sr_loaded = sf.read(audio_path)
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)  # Convert to mono
            if sr_loaded != sr:
                # Resample if needed (requires librosa)
                if HAS_LIBROSA:
                    audio = librosa.resample(audio, orig_sr=sr_loaded, target_sr=sr)
                else:
                    print(f"Warning: Sample rate mismatch ({sr_loaded} vs {sr}). Install librosa for resampling.")
            return audio
        except Exception as e:
            print(f"soundfile failed: {e}")
    
    raise RuntimeError("Could not load audio file. Install librosa: pip install librosa")


def audio_to_mfcc(audio_path, output_path, device='cpu', **mfcc_kwargs):
    """
    Convert audio file to MFCC features and save as .npy file.
    
    Parameters:
    -----------
    audio_path : str
        Path to input audio file
    output_path : str
        Path to output .npy file
    device : str
        'cpu' or GPU device index (default: 'cpu')
    **mfcc_kwargs : dict
        Additional arguments for MFCC_Extractor
    """
    print(f"Loading audio: {audio_path}")
    audio = load_audio_file(audio_path)
    
    print(f"Audio length: {len(audio) / 16000:.2f} seconds")
    
    # Initialize MFCC extractor with default parameters matching the model
    mfcc_extractor = MFCC_Extractor(
        samplerate=16000,
        winlen=0.025,      # 25ms window
        winstep=0.01,      # 10ms step
        numcep=13,         # 13 cepstral coefficients
        nfilt=26,
        device=device,
        **mfcc_kwargs
    )
    
    print("Extracting MFCC features...")
    # Reshape audio to (1, audio_length) for batch processing
    audio_batch = audio.reshape(1, -1)
    mfcc_features = mfcc_extractor(audio_batch)
    
    # Remove batch dimension: (1, num_windows, 13) -> (num_windows, 13)
    mfcc_features = mfcc_features[0]
    
    print(f"MFCC shape: {mfcc_features.shape}")
    print(f"Saving to: {output_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    # Save as .npy file
    np.save(output_path, mfcc_features)
    print(f"✓ Successfully saved MFCC features to {output_path}")


def batch_process(input_dir, output_dir, device='cpu', **mfcc_kwargs):
    """
    Process all audio files in a directory.
    
    Parameters:
    -----------
    input_dir : str
        Directory containing audio files
    output_dir : str
        Directory to save .npy files
    device : str
        'cpu' or GPU device index
    **mfcc_kwargs : dict
        Additional arguments for MFCC_Extractor
    """
    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
    
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"Input directory not found: {input_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend([f for f in os.listdir(input_dir) if f.lower().endswith(ext)])
    
    print(f"Found {len(audio_files)} audio files in {input_dir}")
    
    for audio_file in audio_files:
        input_path = os.path.join(input_dir, audio_file)
        # Change extension to .npy
        output_file = os.path.splitext(audio_file)[0] + '.npy'
        output_path = os.path.join(output_dir, output_file)
        
        try:
            audio_to_mfcc(input_path, output_path, device=device, **mfcc_kwargs)
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")
            continue
    
    print(f"\n✓ Batch processing complete. Processed {len(audio_files)} files.")


def main():
    parser = argparse.ArgumentParser(
        description='Convert audio files to MFCC numpy files for the voice model'
    )
    parser.add_argument('input', nargs='?', help='Input audio file or directory (for batch mode)')
    parser.add_argument('output', nargs='?', help='Output .npy file or directory (for batch mode)')
    parser.add_argument('--batch', action='store_true', 
                       help='Batch process all audio files in input directory')
    parser.add_argument('--device', default='cpu', 
                       help='Device to use: "cpu" or GPU index (default: cpu)')
    
    args = parser.parse_args()
    
    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)
    
    if args.batch:
        batch_process(args.input, args.output, device=args.device)
    else:
        audio_to_mfcc(args.input, args.output, device=args.device)


if __name__ == '__main__':
    main()

