# 🧠 Preset Loader für audio_tagger_pro
# Lädt alle TXT/JSON-Presets aus dem Ordner "presets/" und gibt sie als Dictionary zurück

import os
import json

PRESET_FOLDER = "presets"


def load_presets():
    presets = {}
    if not os.path.exists(PRESET_FOLDER):
        os.makedirs(PRESET_FOLDER)

    for fname in os.listdir(PRESET_FOLDER):
        fpath = os.path.join(PRESET_FOLDER, fname)
        name, ext = os.path.splitext(fname)

        try:
            if ext.lower() == ".json":
                with open(fpath, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "prompt" in data:
                        presets[name] = data["prompt"]
            elif ext.lower() == ".txt":
                with open(fpath, encoding="utf-8") as f:
                    prompt = f.read().strip()
                    if prompt:
                        presets[name] = prompt
        except Exception as e:
            print(f"⚠️ Fehler beim Laden von {fname}: {e}")

    # ⛔️ Für "Choose a Preset (optional)" bewusst keine Vorgabe – soll neutral bleiben
    presets["Choose a Preset (optional)"] = None

    return presets
