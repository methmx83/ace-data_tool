# 📝 Prompt-Editor UI-Komponente
# Zeigt `.mp3` Dateien + zugehörige `_prompt.txt` Dateien zur Bearbeitung

import os
import gradio as gr

AUDIO_DIR = "data"


def list_audio_files():
    files = []
    if os.path.exists(AUDIO_DIR):
        for f in os.listdir(AUDIO_DIR):
            if f.lower().endswith(".mp3"):
                files.append(f)
    return sorted(files)


def load_prompt_for_file(mp3_file):
    if not mp3_file:
        return ""
    name, _ = os.path.splitext(mp3_file)
    prompt_path = os.path.join(AUDIO_DIR, f"{name}_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, encoding="utf-8") as f:
            return f.read()
    return ""


def save_prompt_for_file(mp3_file, new_text):
    if not mp3_file:
        return "Kein Track ausgewählt."
    name, _ = os.path.splitext(mp3_file)
    prompt_path = os.path.join(AUDIO_DIR, f"{name}_prompt.txt")
    try:
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(new_text.strip())
        return "✅ Prompt gespeichert."
    except Exception as e:
        return f"❌ Fehler: {e}"


def prompt_editor_ui():
    with gr.Row():
        track_dropdown = gr.Dropdown(
            choices=list_audio_files(),
            label="🎵 Wähle Track",
            interactive=True
        )
    with gr.Row():
        prompt_box = gr.Textbox(
            label="📝 Prompt bearbeiten",
            lines=2,
            max_lines=4,
            interactive=True
        )
    with gr.Row():
        save_btn = gr.Button("💾 Prompt speichern")
        save_status = gr.Textbox(label="Status", interactive=False)

    # Logik verknüpfen
    track_dropdown.change(fn=load_prompt_for_file, inputs=track_dropdown, outputs=prompt_box)
    save_btn.click(fn=save_prompt_for_file, inputs=[track_dropdown, prompt_box], outputs=save_status)

    return [track_dropdown, prompt_box, save_btn, save_status]
