# 🔁 Überarbeitete generate_tags() mit Stream-Modus & besseren Timeouts
import os
import requests
import re
import sys
import time
import warnings
import json
from tinytag import TinyTag
from scripts.lyrics import load_lyrics
from scripts.bpm import detect_tempo
from scripts.moods import extract_clean_tags

# Unterdrücke bekannte Warnungen
warnings.filterwarnings("ignore", message="No ID3 tag found")
warnings.filterwarnings("ignore", message="It looks like you're loading an mp3")
warnings.filterwarnings("ignore", message="Xing stream size off by more than 1%")
warnings.filterwarnings("ignore", message="Lame tag CRC check failed")

# --- KONFIGURATION (wird später aus config.yaml geladen) ---
INPUT_DIR     = r"Z:\\AI\\projects\\music\\ace-data_tool\\data"
MODEL_NAME    = "deep-x1_q4:latest"  # Kann später aus config.yaml kommen
OLLAMA_URL    = "http://localhost:11434/api/generate"
RETRY_COUNT   = 2  # Weniger Retries, da wir besseres Feedback haben
REQUEST_DELAY = 1.0
TIMEOUT       = 300  # 5 Minuten statt 10 - optimal für dein Modell
# --- ENDE KONFIGURATION ---

def sanitize_filename(name: str, max_length=120) -> str:
    """Bereinigt Dateinamen für Kompatibilität"""
    name = name.encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    name = re.sub(r'[-\s]+', '_', name)
    return name[:max_length]

def generate_tags(file_path, prompt_guidance=None, attempt=1, progress=None):
    """
    Generiert Tags für eine Audiodatei mit LLM
    
    Args:
        file_path: Pfad zur Audiodatei
        prompt_guidance: Optionale Prompt-Ergänzung
        attempt: Aktueller Versuch (für Retries)
        progress: Gradio-Progress-Objekt für UI-Feedback
    
    Returns:
        Liste mit generierten Tags oder None bei Fehler
    """
    filename = os.path.basename(file_path)
    print(f"\n🔧 Starte Tag-Generierung für: {filename}")
    start_time = time.time()
    
    # Metadaten sammeln
    lyrics = load_lyrics(file_path)
    bpm_value = detect_tempo(file_path)
    
    try:
        tag = TinyTag.get(file_path)
        artist = tag.artist or "Unknown"
        title = tag.title or "Unknown"
    except Exception:
        artist, title = "Unknown", "Unknown"
    
    # Lyrics-Excerpt erstellen
    excerpt = f"[LYRICS EXCERPT]\n{lyrics[:250]}[...]\n" if lyrics else ""
    
    # System-Prompt zusammenbauen
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
    
    # Wartezeit vor der Anfrage (exponentiell bei Retries)
    time.sleep(REQUEST_DELAY * (attempt ** 1.5))
    
    try:
        # --- OLLAMA-ANFRAGE MIT STREAM-MODUS ---
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": system_prompt,
                "stream": True,  # WICHTIG: Stream-Modus aktivieren
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0.65,  # Empfohlen für dein Modell
                    "top_p": 0.95         # Empfohlen für dein Modell
                }
            },
            timeout=TIMEOUT,
            stream=True  # WICHTIG: Für iter_lines() benötigt
        )
        resp.raise_for_status()
        
        # --- STREAM-VERARBEITUNG MIT FEEDBACK ---
        raw = ""
        token_count = 0
        
        # Sende Start-Feedback an UI
        if progress:
            progress((None, f"⏳ LLM generiert Tags für {filename}..."))
        
        # Jede Zeile des Streams verarbeiten
        for line in resp.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'response' in chunk:
                        raw += chunk['response']
                        token_count += 1
                        
                        # Jede 15 Tokens Feedback senden
                        if token_count % 15 == 0 and progress:
                            progress((None, f"⏳ LLM generiert Tags... (Token {token_count})"))
                except json.JSONDecodeError:
                    print("⚠️ Fehler beim Parsen eines Stream-Chunks")
        
        # --- TAGS VERARBEITEN ---
        tags = extract_clean_tags(raw)
        
        # BPM-Tag sicherstellen
        if bpm_value:
            bpm_tag = f"bpm-{bpm_value}"
            if bpm_tag not in tags:
                tags.append(bpm_tag)
            # Stelle sicher, dass BPM-Tag am Anfang steht
            if bpm_tag in tags and tags.index(bpm_tag) > 4:
                tags.remove(bpm_tag)
                tags.insert(0, bpm_tag)
        
        # --- ERGEBNIS AUSGEBEN ---
        duration = time.time() - start_time
        print(f"✅ Tags in {duration:.2f}s: {', '.join(tags[:5])}...")
        
        if progress:
            progress((None, f"✅ Tags generiert für {filename} in {duration:.2f}s"))
            
        return tags
        
    except Exception as e:
        error_msg = f"❌ Fehler bei {filename} (Versuch {attempt}/{RETRY_COUNT}): {str(e)}"
        print(error_msg)
        
        # Sende Fehler an UI
        if progress and attempt <= RETRY_COUNT:
            progress((None, f"⚠️ {error_msg}"))
        
        # Retry, wenn möglich
        if attempt <= RETRY_COUNT:
            print(f"➡️ Erneuter Versuch in 2 Sekunden...")
            time.sleep(2)
            return generate_tags(file_path, prompt_guidance, attempt + 1, progress)
        
        # Endgültiger Fehler
        print(f"❌ Abbruch nach {RETRY_COUNT} Versuchen")
        if progress:
            progress((None, f"❌ Abbruch nach {RETRY_COUNT} Versuchen für {filename}"))
            
        return None

def save_tags(file_path, tags):
    """Speichert generierte Tags in eine Datei"""
    if not tags:
        return
    
    out_path = os.path.splitext(file_path)[0] + "_prompt.txt"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(", ".join(tags))
        return True
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Tags für {file_path}: {e}")
        return False