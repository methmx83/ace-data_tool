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
import subprocess
from shared_logs import LOGS, log_message

log_message("... Music Tagger Script loaded ✅")

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
            log_message("💡 Ollama context reset")
            return True
        log_message(f"⚠️ Reset failed: Status {response.status_code}")
    except Exception as e:
        log_message(f"❌ Reset error: {str(e)}")
    return False

def unload_model():
    """Unloads the active model from memory"""
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
            log_message(f"♻️ Model {MODEL_NAME} unloaded")
            return True
    except Exception as e:
        log_message(f"❌ Model unloading failed: {str(e)}")
    return False

def load_model():
    """Loads the model into memory (warm start)"""
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
            log_message(f"✅ Model {MODEL_NAME} reloaded")
            return True
    except Exception as e:
        log_message(f"❌ Model loading failed: {str(e)}")
    return False

def reload_model():
    """Unloads and reloads the model"""
    log_message(f"🔄 Trying model reload for {MODEL_NAME}...")
    if unload_model():
        time.sleep(2)  # Short pause for RAM release
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
    # Save tags to a separate file
    out = os.path.splitext(file_path)[0] + "_prompt.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(", ".join(tags))

    # Clean up the lyrics file
    lyrics_file = os.path.splitext(file_path)[0] + "_lyrics.txt"
    from include.clean_lyrics import bereinige_datei
    bereinige_datei(lyrics_file)

def generate_tags(file_path, prompt_guidance=None, attempt=1):

    # Clean up the lyrics file before tag generation
    lyrics_file = os.path.splitext(file_path)[0] + "_lyrics.txt"
    from include.clean_lyrics import bereinige_datei

    log_message(f"🔧 Cleaning lyrics file: {lyrics_file}")

    bereinige_datei(lyrics_file)

    log_message(f"📄 Lyrics file cleaned: {lyrics_file}")
    log_message(f"\n⏳ Starting tag generation for: {os.path.basename(file_path)}")
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

    # User prompt for clear task definition
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

    # Dynamic timeout (increases with attempts)
    timeout = 60 * min(attempt, 5)  # Max 5 minutes

    try:
        resp = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=timeout
        )
        resp.raise_for_status()
        
        # Response processing
        response_data = resp.json()
        raw = response_data.get("message", {}).get("content", "")
        
        if not raw:
            raise ValueError("Empty response from model")
            
        tags = extract_clean_tags(raw)

        # Ensure BPM tag
        if bpm_value:
            bpm_tag = f"bpm-{bpm_value}"
            if bpm_tag not in tags:
                tags.append(bpm_tag)
            if bpm_tag in tags and tags.index(bpm_tag) > 4:
                tags.remove(bpm_tag)
                tags.insert(0, bpm_tag)

        duration = time.time() - start_time
        log_message(f"✅ Tags generated in {duration:.2f}s: 🔥 {', '.join(tags[:5])}...")
        return tags

    except Exception as e:
        if attempt <= RETRY_COUNT:
            log_message(f"❌ Error (Attempt {attempt}/{RETRY_COUNT}): {str(e)}")
            # Escalating error handling
            if attempt == 1:
                reset_ollama_context()
            elif attempt == 2:
                reload_model()
            elif attempt >= 3:
                # ENHANCED MODEL RELOAD
                log_message("🔄 Trying enhanced model reload...")
                try:
                    # 1. Explicitly unload model
                    unload_model()
                    time.sleep(3)

                    # 2. Reload model with longer timeout
                    load_model()
                    
                    # 3. Additional context reset
                    reset_ollama_context()
                    log_message("🌟 Model and context completely renewed")
                except Exception as reload_error:
                    log_message(f"⚠️ Enhanced reload failed: {reload_error}")

            time.sleep(5 * attempt)  # Progressive delay
            return generate_tags(file_path, prompt_guidance, attempt + 1)

        log_message(f"❌ Final error at {filename}: {e}")
        return None

# Test function for direct execution
if __name__ == "__main__":
    log_message("🔍 Testing Ollama connection...")
    try:
        resp = requests.get(OLLAMA_URL.replace('/api/generate', ''), timeout=5)
        log_message(f"✅ Ollama is running (Status {resp.status_code})")
    except Exception as e:
        log_message(f"❌ Ollama connection error: {e}")
        log_message("🔄 Restarting Ollama server...")
        try:
            subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            time.sleep(15)
            log_message("✅ Ollama server started")
        except:
            log_message("⛔ Ollama could not be started")