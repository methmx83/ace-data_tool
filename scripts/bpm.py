import numpy as np
import librosa
from librosa.feature import rhythm
import re
import os
import sys
from shared_logs import LOGS, log_message


    # Main message when loading the file
log_message("... BPM calculation Script loaded ✅")

def detect_tempo(file_path):
    try:
        # Installiere resampy falls nötig
        try:
            import resampy
        except ImportError:
            log_message("⚠️ Resampy not installed - install now...")
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
        log_message(f"⚠️ Tempo detection error: {str(e)}")
        # Fallback: Versuche Tempo aus Dateinamen zu extrahieren
        match = re.search(r'bpm[_-]?(\d{2,3})', os.path.basename(file_path), re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

def adjust_bpm(tempo):
    """Adjusts BPM values to ensure they are within a reasonable range."""
    if tempo is None or tempo <= 0:
        log_message("⚠️ Invalid BPM value: adjustment not possible")
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
    adjusted_bpm = adjust_bpm(detected_tempo)
    
    # Ausgabe der Nachricht nach der BPM-Berechnung
    log_message(f"✅ BPM calculated for {file_path}: {adjusted_bpm}")
    
    return adjusted_bpm
