import torchaudio
import os

# Configuration
input_dir = '../'          # Directory containing .mp3 files (two levels higher)
output_dir = '../wav/files' # Directory to save .wav files
preserve_structure = True  # True to preserve directory structure, False to flatten

def convert_mp3_to_wav(input_path, output_path):
    """Convert an MP3 file to WAV format with a 32kHz sample rate."""
    if os.path.exists(output_path):
        print(f"Skipping {output_path} (already exists)")
        return
    waveform, sr = torchaudio.load(input_path)
    waveform = torchaudio.transforms.Resample(sr, 32000)(waveform)
    torchaudio.save(output_path, waveform, 32000)
    print(f"Converted {input_path} to {output_path}")

# Get absolute paths for comparison
input_dir_abs = os.path.abspath(input_dir)
output_dir_abs = os.path.abspath(output_dir)

# Create output directory if it doesn’t exist
os.makedirs(output_dir, exist_ok=True)

# Traverse input_dir, excluding output_dir to prevent recursive processing
for root, dirs, files in os.walk(input_dir):
    root_abs = os.path.abspath(root)
    # Skip output_dir and its subdirectories
    if root_abs == output_dir_abs or root_abs.startswith(output_dir_abs + os.sep):
        dirs[:] = []  # Prevent traversal into subdirectories
        continue      # Skip processing files in this directory
    # Process only .mp3 files
    for filename in files:
        if filename.endswith('.mp3'):
            input_filepath = os.path.join(root, filename)
            output_filename = filename.replace('.mp3', '.wav')
            if preserve_structure:
                # Preserve directory structure under output_dir
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                os.makedirs(output_subdir, exist_ok=True)
                output_filepath = os.path.join(output_subdir, output_filename)
            else:
                # Flatten all files into output_dir
                output_filepath = os.path.join(output_dir, output_filename)
            convert_mp3_to_wav(input_filepath, output_filepath)