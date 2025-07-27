import numpy as np
import librosa
from librosa.feature import rhythm
import re
import os
import sys

def detect_tempo(file_path):
    try:
        # Installiere resampy falls nötig
        try:
            import resampy
        except ImportError:
            print("⚠️ Resampy nicht installiert - installiere jetzt...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "resampy"])
            import resampy
            
        y, sr = librosa.load(
            file_path,
            duration=30,
            mono=True,
            sr=22050,
            res_type='kaiser_fast'
        )
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
        tempo = rhythm.tempo(onset_envelope=onset_env, sr=sr)[0]
        return int(round(tempo))
    
    except Exception as e:
        print(f"⚠️ Tempo-Erkennungsfehler: {str(e)}")
        # Fallback: Versuche Tempo aus Dateinamen zu extrahieren
        match = re.search(r'bpm[_-]?(\d{2,3})', os.path.basename(file_path), re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

def adjust_bpm(tempo):
    """Passt BPM-Werte an, um sicherzustellen, dass sie in einem sinnvollen Bereich liegen."""
    if tempo is None or tempo <= 0:
        print("⚠️ Ungültiger BPM-Wert: Anpassung nicht möglich")
        return None

    # Konvertiere zu float für präzise Berechnungen
    temp = float(tempo)

    # Wenn BPM über 140 liegt, halbiere den Wert
    while temp > 140:
        temp //= 2.0
    # Wenn BPM unter 60 liegt, verdopple den Wert
    while temp < 60:
        temp *= 2
    return int(round(temp))

def get_bpm(file_path):
    detected_tempo = detect_tempo(file_path)
    return adjust_bpm(detected_tempo)
