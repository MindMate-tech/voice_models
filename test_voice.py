#!/usr/bin/env python3
"""
Simple script to test a trained model on a single voice audio file.

Usage:
    python test_voice.py <audio_file> [model_path]
    
Example:
    python test_voice.py test_audio.wav
    python test_voice.py test_audio.mp3 pt_files/cnn_norm_vs_ad_github_test_with_loss_weights_1.0_1.0/cnn_norm_vs_ad_github_test_with_loss_weights_1.0_1.0_0_72901_1_2025-11-08_17:06:14.833328_epochs.pt
"""

import sys
import os
import argparse
import numpy as np
import torch

# Add azrt2021 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'azrt2021'))

from azrt2021.model import Model
from azrt2021.tcn import TCN
from preprocess_audio import audio_to_mfcc, load_audio_file
from azrt2021.mfcc import MFCC_Extractor


def predict_voice(audio_path, model_path=None, device='cpu'):
    """
    Predict dementia probability for a voice audio file.
    
    Parameters:
    -----------
    audio_path : str
        Path to audio file (MP3, WAV, etc.)
    model_path : str, optional
        Path to trained model .pt file. If None, uses the most recent model.
    device : str
        Device to use: 'cpu' or 'cuda:0' (default: 'cpu')
    
    Returns:
    --------
    probability : float
        Probability of dementia (0.0 to 1.0)
        - Higher values indicate higher likelihood of dementia
        - Lower values indicate normal/healthy voice
    """
    print("=" * 60)
    print("Voice Dementia Detection - Inference")
    print("=" * 60)
    
    # Step 1: Convert audio to MFCC features
    print(f"\n[1/4] Loading and preprocessing audio: {audio_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Load audio
    audio = load_audio_file(audio_path)
    print(f"   Audio length: {len(audio) / 16000:.2f} seconds")
    
    # Extract MFCC features
    mfcc_extractor = MFCC_Extractor(
        samplerate=16000,
        winlen=0.025,
        winstep=0.01,
        numcep=13,
        nfilt=26,
        device=device
    )
    
    audio_batch = audio.reshape(1, -1)
    mfcc_features = mfcc_extractor(audio_batch)[0]  # Remove batch dimension
    print(f"   MFCC features shape: {mfcc_features.shape}")
    
    # Step 2: Find model file if not provided
    if model_path is None:
        print(f"\n[2/4] Finding trained model...")
        # Look for the most recent model in pt_files directory
        pt_files_dir = os.path.join(os.path.dirname(__file__), 'azrt2021', 'pt_files')
        if os.path.isdir(pt_files_dir):
            # Find all .pt files
            pt_files = []
            for root, dirs, files in os.walk(pt_files_dir):
                for file in files:
                    if file.endswith('.pt') and 'tmp' not in file:
                        pt_files.append(os.path.join(root, file))
            
            if pt_files:
                # Sort by modification time, get most recent
                pt_files.sort(key=os.path.getmtime, reverse=True)
                model_path = pt_files[0]
                print(f"   Using model: {os.path.basename(model_path)}")
            else:
                raise FileNotFoundError(
                    f"No trained model found in {pt_files_dir}. "
                    f"Please train a model first or specify model_path."
                )
        else:
            raise FileNotFoundError(
                f"Model directory not found: {pt_files_dir}. "
                f"Please specify model_path."
            )
    else:
        print(f"\n[2/4] Loading specified model: {model_path}")
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Step 3: Load model
    print(f"\n[3/4] Loading trained model...")
    n_concat = 10
    neural_network = TCN(device)
    model_obj = Model(n_concat=n_concat, device=device, nn=neural_network)
    model_obj.load_model(model_path)
    model_obj.nn.eval()  # Set to evaluation mode
    print(f"   Model loaded successfully")
    
    # Step 4: Run inference
    print(f"\n[4/4] Running inference...")
    
    # Prepare data in the format the model expects
    # The model expects a list of numpy arrays (one per sample)
    mfcc_list = [mfcc_features]
    
    # Reformat using the model's reformat function (this will pad to 16384 frames)
    model_obj.nn.reformat(mfcc_list, n_concat)
    
    # Get prediction
    with torch.no_grad():
        scores = model_obj.nn.get_scores(mfcc_list)
        # scores is a tensor of shape (1, 2) - [class_0_score, class_1_score]
        # Convert to probability using softmax
        probs = torch.softmax(scores, dim=1)
        # NOTE: Based on user feedback, the labels appear to be flipped
        # Flipping the interpretation: class 0 = Dementia, class 1 = Normal
        dementia_prob = probs[0][0].item()    # Probability of class 0 (dementia - FLIPPED)
        normal_prob = probs[0][1].item()      # Probability of class 1 (normal - FLIPPED)
    
    # Step 5: Display results
    print("\n" + "=" * 60)
    print("PREDICTION RESULTS")
    print("=" * 60)
    print(f"Normal (Healthy) Probability:     {normal_prob:.4f} ({normal_prob*100:.2f}%)")
    print(f"Dementia Probability:             {dementia_prob:.4f} ({dementia_prob*100:.2f}%)")
    print("=" * 60)
    
    if dementia_prob > 0.5:
        print(f"\n⚠️  WARNING: High dementia probability detected ({dementia_prob*100:.2f}%)")
        print("   This suggests possible signs of dementia in the voice.")
    else:
        print(f"\n✅ Normal voice detected ({normal_prob*100:.2f}% confidence)")
        print("   The voice appears to be within normal range.")
    
    print("\nNote: This is a screening tool and should not replace professional medical diagnosis.")
    print("=" * 60)
    
    return dementia_prob


def main():
    parser = argparse.ArgumentParser(
        description='Test a trained voice dementia detection model on a single audio file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with auto-detected model
  python test_voice.py test_audio.wav
  
  # Test with specific model
  python test_voice.py test_audio.mp3 azrt2021/pt_files/.../model.pt
  
  # Use CPU explicitly
  python test_voice.py test_audio.wav --device cpu
        """
    )
    parser.add_argument('audio_file', 
                       help='Path to audio file (MP3, WAV, FLAC, etc.)')
    parser.add_argument('model_path', nargs='?', default=None,
                       help='Path to trained model .pt file (optional, uses most recent if not specified)')
    parser.add_argument('--device', default='cpu',
                       help='Device to use: "cpu" or "cuda:0" (default: cpu)')
    
    args = parser.parse_args()
    
    try:
        probability = predict_voice(args.audio_file, args.model_path, args.device)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

