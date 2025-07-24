# 🔁 Erweiterte generate_tags() mit Prompt-Guidance

import os
import requests
import re
import sys
import time
import warnings
import shutil
import unicodedata

from tinytag import TinyTag
import numpy as np
import librosa
from librosa.feature import rhythm

from scripts.lyrics import load_lyrics
from scripts.bpm import detect_tempo
from scripts.moods import extract_clean_tags

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

INPUT_DIR     = r"Z:\\AI\projects\music\ace-data_tool\data"
MODEL_NAME    = "deep-x1_q8:latest"
OLLAMA_URL    = "http://localhost:11434/api/generate"
RETRY_COUNT   = 3
REQUEST_DELAY = 1.5

def sanitize_filename(name: str, max_length=120) -> str:
    name = unicodedata.normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    name = re.sub(r'[-\s]+', '_', name)
    return name[:max_length]

def generate_tags(file_path, prompt_guidance=None, attempt=1):
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

    excerpt = f"[LYRICS EXCERPT]\n{lyrics[:250]}[...]\n\n" if lyrics else ""

    system_prompt = f"""
[ROLE]
You are an expert music tagging AI.

[METADATA]
Artist: {artist}
Title: {title}
BPM: {bpm_value or 'Unknown'}

{excerpt}[STYLE GUIDANCE]
{prompt_guidance or 'Use your best judgment based on the audio.'}

[RULES]
1. ALWAYS include 'bpm-xxx' if BPM known.
2. Generate 10-12 comma-separated tags.
3. Use lowercase hyphenated format.
4. Prioritize tags from Moods.md.
5. Max 2 genre tags.
6. Include at least one from each category: vocal type, instruments, mood.
7. For rap: include at least one rap-style tag.

[EXAMPLE]
bpm-92, male-vocal, synthesizer, drums, aggressive, gangsta-rap, german-rap, bass-heavy, dark, street
"""

    time.sleep(REQUEST_DELAY * attempt)
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": system_prompt, "stream": False, "options": {"num_ctx": 2048}},
            timeout=1800
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "")
        tags = extract_clean_tags(raw)

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
            time.sleep(2)
            return generate_tags(file_path, prompt_guidance, attempt + 1)
        print(f"❌ Fehler bei {filename}: {e}")
        return None

def save_tags(file_path, tags):
    if not tags:
        return
    out = os.path.splitext(file_path)[0] + "_prompt.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(", ".join(tags))
