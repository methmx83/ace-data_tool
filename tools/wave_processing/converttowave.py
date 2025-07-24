import torchaudio
import os

input_dir = '../Activision/Timothy Seals - A New Dawn (Cover Edition)'
output_dir = '../Activision/wav/files'

os.makedirs(output_dir, exist_ok=True)
for filename in os.listdir(input_dir):
    if filename.endswith('.mp3'):
        filepath = os.path.join(input_dir, filename)
        waveform, sr = torchaudio.load(filepath)
        waveform = torchaudio.transforms.Resample(sr, 32000)(waveform)
        output_path = os.path.join(output_dir, filename.replace('.mp3', '.wav'))
        torchaudio.save(output_path, waveform, 32000)