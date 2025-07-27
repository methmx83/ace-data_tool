# 🔁 Erweiterte generate_tags() mit Prompt-Guidance und stabiler API-Integration

import os
import requests
import re
import sys
import time
import warnings
import shutil
import unicodedata
import json

from tinytag import TinyTag
import numpy as np
import librosa
from librosa.feature import rhythm

from scripts.lyrics import load_lyrics
from scripts.bpm import detect_tempo
from scripts.moods import extract_clean_tags
from include.clean_lyrics import main as clean_lyrics_main

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from collections import Counter

nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)
sia = SentimentIntensityAnalyzer()
STOPWORDS = set(stopwords.words('english'))

warnings.filterwarnings("ignore", message="No ID3 tag found")
warnings.filterwarnings("ignore", message="It looks like you're loading an mp3")
warnings.filterwarnings("ignore", message="Lame tag CRC check failed")
warnings.filterwarnings("ignore", module="librosa")
warnings.filterwarnings("ignore", message="Xing stream size off by more than 1%")

# Lade Konfiguration aus JSON-Datei
config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

INPUT_DIR     = config['input_dir']
MODEL_NAME    = config['model_name']
OLLAMA_URL    = config['ollama_url']
RETRY_COUNT   = config['retry_count']
REQUEST_DELAY = config['request_delay']

# Konvertiere URLs für API-Endpoints
OLLAMA_CHAT_URL = OLLAMA_URL.replace('/generate', '/chat')
OLLAMA_RESET_URL = OLLAMA_URL.replace('/generate', '/reset')

# 🔄 Modell-Management-Funktionen
def reset_ollama_context():
    """Setzt den Kontext des LLMs zurück"""
    try:
        response = requests.post(OLLAMA_RESET_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Ollama-Kontext zurückgesetzt")
            return True
        print(f"⚠️ Reset fehlgeschlagen: Status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Reset-Fehler: {str(e)}")
    return False

def unload_model():
    """Entlädt das aktive Modell aus dem Speicher"""
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": MODEL_NAME,
                "messages": [],
                "keep_alive": 0  # 0 = sofort entladen
            },
            timeout=10
        )
        if response.json().get("done_reason") == "unload":
            print(f"♻️ Modell {MODEL_NAME} entladen")
            return True
    except Exception as e:
        print(f"⚠️ Modell-Entladung fehlgeschlagen: {str(e)}")
    return False

def load_model():
    """Lädt das Modell in den Speicher (warm start)"""
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": MODEL_NAME,
                "messages": []  # Leere Nachricht = nur laden
            },
            timeout=30
        )
        if response.json().get("done_reason") == "load":
            print(f"♨️ Modell {MODEL_NAME} neu geladen")
            return True
    except Exception as e:
        print(f"⚠️ Modell-Ladung fehlgeschlagen: {str(e)}")
    return False

def reload_model():
    """Entlädt und lädt das Modell neu"""
    print(f"🔄 Versuche Modell-Reload für {MODEL_NAME}...")
    if unload_model():
        time.sleep(2)  # Kurze Pause für RAM-Freigabe
    return load_model()

def sanitize_filename(name: str, max_length=120) -> str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    name = re.sub(r'[-\s]+', '_', name)
    return name[:max_length]

def save_tags(file_path, tags):
    if not tags:
        return
    # Speichere die Tags in eine separate Datei
    out = os.path.splitext(file_path)[0] + "_prompt.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(", ".join(tags))

    # Bereinige die Lyrics-Datei
    lyrics_file = os.path.splitext(file_path)[0] + "_lyrics.txt"
    from include.clean_lyrics import bereinige_datei
    bereinige_datei(lyrics_file)

def generate_tags(file_path, prompt_guidance=None, attempt=1):
    
    # Bereinige die Lyrics-Datei vor der Tag-Generierung
    lyrics_file = os.path.splitext(file_path)[0] + "_lyrics.txt"
    from include.clean_lyrics import bereinige_datei
    bereinige_datei(lyrics_file)

    print(f"\n🔧 Starte Tag-Generierung für: {os.path.basename(file_path)}")
    start_time = time.time()

    filename = os.path.basename(file_path)
    lyrics = load_lyrics(file_path)
    bpm_value = detect_tempo(file_path)

    try:
        tag = TinyTag.get(file_path)
        artist = tag.artist or "Unknown"
        title = tag.title or "Unknown"
    except Exception:
        artist, title = "Unknown", "Unknown"

    excerpt = f"[LYRICS EXCERPT]\n{lyrics[:300]}[...]\n\n" if lyrics else ""

    # System-Prompt mit klarer Struktur
    system_prompt = f"""
### ROLE
You are an expert music tagging AI

### METADATA
Artist: {artist}
Title: {title}
BPM: {bpm_value or 'Unknown'}

{excerpt}### STYLE GUIDANCE
{prompt_guidance or 'Use your best judgment based on the audio'}

### RULES
1. ALWAYS include 'bpm-xxx' if BPM known
2. Generate 12-14 comma-separated tags
3. Use lowercase hyphenated format
4. Prioritize tags from Moods.md
5. Max 2 genre tags
6. Include at least one from each category: vocal type, instruments, mood , rap styles
7. For rap: include at least one rap-styles tag

### EXAMPLE
bpm-92, male/ female-vocal, synthesizer, drums, aggressive, gangsta-rap, german-rap, bass-heavy, dark, street
"""

    # User-Prompt für klare Aufgabenstellung
    user_prompt = "Generate 12 music tags based on the rules above. Output ONLY comma-separated tags."

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {"num_ctx": 4096}
    }

    # Dynamisches Timeout (steigt mit Versuchen)
    timeout = 60 * min(attempt, 5)  # Max 5 Minuten

    try:
        resp = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=timeout
        )
        resp.raise_for_status()
        
        # Antwortverarbeitung
        response_data = resp.json()
        raw = response_data.get("message", {}).get("content", "")
        
        if not raw:
            raise ValueError("Empty response from model")
            
        tags = extract_clean_tags(raw)

        # BPM-Tag sicherstellen
        if bpm_value:
            bpm_tag = f"bpm-{bpm_value}"
            if bpm_tag not in tags:
                tags.append(bpm_tag)
            if bpm_tag in tags and tags.index(bpm_tag) > 4:
                tags.remove(bpm_tag)
                tags.insert(0, bpm_tag)

        duration = time.time() - start_time
        print(f"✅ Tags in {duration:.2f}s: {', '.join(tags[:5])}...")
        return tags

    except Exception as e:
        if attempt <= RETRY_COUNT:
            print(f"⚠️ Fehler (Versuch {attempt}/{RETRY_COUNT}): {str(e)}")
            # Eskalierende Fehlerbehandlung
            if attempt == 1:
                reset_ollama_context()
            elif attempt == 2:
                reload_model()
            elif attempt >= 3:
                # VERSTÄRKTER MODELL-RELOAD
                print("🔄 Verstärkter Modell-Reload...")
                try:
                    # 1. Modell explizit entladen
                    unload_model()
                    time.sleep(3)
                    
                    # 2. Modell neu laden mit längerem Timeout
                    load_model()
                    
                    # 3. Zusätzlicher Kontext-Reset
                    reset_ollama_context()
                    print("✅ Modell und Kontext vollständig erneuert")
                except Exception as reload_error:
                    print(f"⚠️ Verstärkter Reload fehlgeschlagen: {reload_error}")
            
            time.sleep(5 * attempt)  # Progressive Verzögerung
            return generate_tags(file_path, prompt_guidance, attempt + 1)
        
        print(f"❌ Endgültiger Fehler bei {filename}: {e}")
        return None

# Testfunktion bei direkter Ausführung
if __name__ == "__main__":
    print("🔍 Teste Ollama-Verbindung...")
    try:
        resp = requests.get(OLLAMA_URL.replace('/api/generate', ''), timeout=5)
        print(f"✅ Ollama läuft (Status {resp.status_code})")
    except Exception as e:
        print(f"❌ Ollama-Verbindungsfehler: {e}")
        print("🔄 Starte Ollama-Server neu...")
        try:
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            time.sleep(15)
            print("✅ Ollama-Server gestartet")
        except:
            print("⛔ Ollama konnte nicht gestartet werden")