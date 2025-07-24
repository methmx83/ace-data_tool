# 🔁 Erweiterte app.py mit Mood + Genre + Prompt-Guidance-Unterstützung
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))  # webui/
project_root = os.path.dirname(current_dir)              # ace-data_tool/
sys.path.append(os.path.join(project_root, 'scripts'))
sys.path.append(os.path.join(project_root, 'include'))
sys.path.append(os.path.join(project_root, 'tools'))

import shutil
import gradio as gr
from prompt_editor import prompt_editor_ui
from tinytag import TinyTag
from preset_loader import load_presets
from scripts.lyrics import load_lyrics, fetch_and_save_lyrics
from scripts.bpm import get_bpm
from scripts.tagger import generate_tags, save_tags


AUDIO_DIR = "data"

# Lade Genre-Presets
GENRE_PRESETS = load_presets()

def process_file(mp3_path: str, overwrite_lyrics: bool = False, prompt_guidance: str = "") -> str:
    base, _ = os.path.splitext(mp3_path)
    tag = TinyTag.get(mp3_path)
    artist = tag.artist or "Unknown"
    title = tag.title or "Unknown"

    lyrics_path = f"{base}_lyrics.txt"
    if not os.path.exists(lyrics_path) or overwrite_lyrics:
        fetch_and_save_lyrics(artist, title, lyrics_path)
    lyrics = load_lyrics(mp3_path) or "–"

    bpm = get_bpm(mp3_path) or "–"
    tags = generate_tags(mp3_path, prompt_guidance=prompt_guidance)
    save_tags(mp3_path, tags)

    return (
        f"🎵 {os.path.basename(mp3_path)}\n"
        f"Artist: {artist}\nTitle: {title}\nBPM: {bpm}\nTags: {', '.join(tags[:8])}...\n"
        f"✓ Saved lyrics and prompt"
    )

def process_all_ui(overwrite_lyrics: bool = False, genre: str = "Custom", mood: float = 0.0, user_prompt: str = "", progress=gr.Progress()) -> str:
    if user_prompt.strip():
        prompt_guidance = user_prompt.strip()
    else:
        base = GENRE_PRESETS.get(genre) or ""
        mood_tag = "happy" if mood > 0.3 else "sad" if mood < -0.3 else "neutral"
        prompt_guidance = f"{base}, {mood_tag}".strip(", ")

    log = []
    audio_files = []
    for root, _, files in os.walk(AUDIO_DIR):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                audio_files.append(os.path.join(root, file))

    for file_path in progress.tqdm(audio_files, desc="Verarbeite Songs"):
        try:
            log.append(process_file(file_path, overwrite_lyrics=overwrite_lyrics, prompt_guidance=prompt_guidance))
        except Exception as e:
            log.append(f"✗ {os.path.basename(file_path)}: {e}")
    return "\n\n---\n\n".join(log)

def export_to_folder(destination: str) -> str:
    if not os.path.exists(destination):
        try:
            os.makedirs(destination, exist_ok=True)
        except Exception as e:
            return f"❌ Zielordner konnte nicht erstellt werden:\n{e}"

    files_copied = 0
    for file in os.listdir(AUDIO_DIR):
        if file.endswith((".mp3", "_prompt.txt", "_lyrics.txt")):
            src = os.path.join(AUDIO_DIR, file)
            dst = os.path.join(destination, file)
            try:
                shutil.copy(src, dst)
                files_copied += 1
            except Exception as e:
                return f"❌ Fehler beim Kopieren von {file}: {e}"

    return f"✅ {files_copied} Dateien exportiert nach:\n{destination}"


with gr.Blocks(css="""
body {
  background-color: #121212;
  color: #f0f0f0;
  font-family: 'Segoe UI', sans-serif;
}
.gr-button {
  background: linear-gradient(90deg, #8e2de2, #4a00e0);
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  transition: all 0.3s ease;
}
.gr-button:hover {
  background: linear-gradient(90deg, #4a00e0, #8e2de2);
  transform: scale(1.03);
}
.gr-textbox textarea {
  background-color: #1e1e1e;
  border: 1px solid #444;
  color: #fff;
  font-size: 14px;
  border-radius: 8px;
  text-align: center; /* Zentriert den Text in der Textbox */
}
h1, h2, h3 {
  color: #e0b0ff;
  text-shadow: 0 0 6px rgba(255, 0, 255, 0.2);
}
""") as demo:

    gr.Markdown("""# 🎧 Audio Tagger Pro
**Tag your tracks with lyrics, BPM and moods – fully automated.**""")

    # Hier den neuen Tab für den Prompt Editor einfügen
    with gr.Tab("📝 Prompt Editor"):
        prompt_editor_ui()

    with gr.Row():
        lyrics_checkbox = gr.Checkbox(label="Lyrics überschreiben", value=False)
        genre_dropdown = gr.Dropdown(label="🎼 Genre-Preset", choices=list(GENRE_PRESETS.keys()), value="Choose a Preset (optional)")
        mood_slider = gr.Slider(label="🎭 Mood: Sad ↔ Happy", minimum=-1.0, maximum=1.0, value=0.0, step=0.1)

    prompt_input = gr.Textbox(label="✍️ Manueller Prompt (optional)", placeholder="orchestral, melancholic, strings, 80 bpm", lines=1)

    start_button = gr.Button("Start Tagging")
    output_box = gr.Textbox(label="Process Log", lines=15, interactive=False)

    start_button.click(
        fn=process_all_ui,
        inputs=[lyrics_checkbox, genre_dropdown, mood_slider, prompt_input],
        outputs=output_box
    )

    with gr.Row():
        export_folder = gr.Textbox(label="Zielordner für ACE-Step Export", value="Z:/AI/projects/music/ace-step/data/")
        export_button = gr.Button("📤 Exportiere nach Ordner")
        export_button.click(fn=export_to_folder, inputs=export_folder, outputs=output_box)

def main():
    demo.launch(server_name="127.0.0.1", server_port=7860)

if __name__ == "__main__":
    main()