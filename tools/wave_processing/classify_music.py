import os
import json
import librosa
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm

# Load the pre-trained model and feature extractor for genre prediction
model_name = "sanchit-gandhi/distilhubert-finetuned-gtzan"
feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForAudioClassification.from_pretrained(model_name)

# Directory containing .wav files and labels.csv
AUDIO_DIR = "files"

# List of genres the model can predict
genres = ["blues", "classical", "country", "disco", "hiphop", "jazz", "metal", "pop", "reggae", "rock"]

# Load labels.csv into a dictionary
def load_labels():
    labels_csv = os.path.join(AUDIO_DIR, "labels.csv")
    if not os.path.exists(labels_csv):
        raise FileNotFoundError(f"{labels_csv} not found in {AUDIO_DIR}.")
    df = pd.read_csv(labels_csv)
    if 'filename' not in df.columns or 'label' not in df.columns:
        raise ValueError("labels.csv must contain 'filename' and 'label' columns.")
    return dict(zip(df['filename'], df['label']))

# Function to process each .wav file
def process_file(filename, labels_dict):
    file_path = os.path.join(AUDIO_DIR, filename)
    try:
        # Load the audio file with its native sample rate
        audio, sr = librosa.load(file_path, sr=None)
        
        # Extract duration
        duration = librosa.get_duration(y=audio, sr=sr)
        
        # Extract tempo
        tempo = librosa.beat.tempo(y=audio, sr=sr)[0]
        
        # Preprocess audio for the model (resample to 16kHz if needed)
        target_sr = 16000
        if sr != target_sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
            sr_model = target_sr
        else:
            sr_model = sr
        inputs = feature_extractor(audio, sampling_rate=sr_model, return_tensors="pt")
        
        # Predict genre using the model
        with torch.no_grad():
            logits = model(**inputs).logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1).squeeze().numpy()
        predicted_genre = genres[np.argmax(probabilities)]
        
        # Get the original label from labels.csv if available
        original_label = labels_dict.get(filename, "No description available")
        
        # Create a detailed description
        description = f"{original_label}. {predicted_genre}, {tempo:.2f} BPM, {sr} Hz"
        
        # Create metadata dictionary
        metadata = {
            "duration": round(duration, 3),
            "description": description,
            "genre": predicted_genre,
            "tempo": round(tempo, 2),
            "sample_rate": sr
        }
        
        # Save to JSON file
        json_filename = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(AUDIO_DIR, json_filename)
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"Saved {json_path}")
    except librosa.LibrosaError as e:
        print(f"Audio loading error for {filename}: {e}")
    except Exception as e:
        print(f"Unexpected error processing {filename}: {e}")

# Main execution
if __name__ == "__main__":
    labels_dict = load_labels()
    for filename in tqdm([f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]):
        process_file(filename, labels_dict)