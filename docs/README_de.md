
<h1 align="center">🎵 ACE-Step Data-Tool</h1>
<p align="center">
  <strong>Automatisiertes Tool zur Erstellung von Musik-Datensätzen für ACE-Step</strong><br>
  <em>Lyrics, Tags & BPM direkt aus Audiodateien generieren – komplett lokal mit Ollama & Gradio</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/methmx83/ace-data_tool?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/license/methmx83/ace-data_tool" alt="License">
  <img src="https://img.shields.io/badge/Status-Stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Ollama-Compatible-blue" alt="Ollama compatible">
</p>

<p align="center">
  <img src="./docs/Screenshot.png" alt="ACE-Step Data Tool Screenshot" width="80%">
</p>

---

## ✨ Features

- 🎙️ **Lyrics Detection** – automatisch über Genius.com
- 🧠 **LLM-basiertes Prompt-Tagging** (Genre, Mood, BPM, Vocals, Style)
- 🕺 **BPM-Erkennung** über Librosa
- 🖥️ **Moderne WebUI** mit Mood-Slider, Presets & Freitext
- 🗂️ **Exportfunktion** für ACE-Step-Datensätze
- 🔁 **Wiederholbares Processing mit Fallback-Logik**

---

## ⚙️ Installation

```bash
# 1. Repo klonen
git clone https://github.com/methmx83/ace-data_tool.git
cd ace-data_tool

# 2. Conda-Umgebung erstellen
conda create -n ace-data_env python=3.13 -y
conda activate ace-data_env

# 3. Abhängigkeiten installieren
pip install -e .

# 4. NLTK-Daten herunterladen (einmalig)
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('stopwords')"

# 5. Ollama installieren & Modell laden
ollama pull deep-x1_q4
````

---

## 🚀 Quickstart

```bash
# Starte die WebUI (lokal)
ace-data
```

👉 Danach öffnet sich `http://localhost:7860` im Browser

🎛️ Wähle:

* 🎵 Deinen Audio-Ordner (`data/`)
* 🎭 Genre-Preset oder Mood
* 🧠 Optional: eigene Prompt-Zusätze
* ✅ Starte die Verarbeitung!

Ergebnis:

```
song.mp3
song_lyrics.txt   → Künstler, Titel, Lyrics
song_prompt.txt   → Tags wie: bpm-90, dark, 90s, male-vocal, boom-bap
```

---

## 🖥️ Empfohlene Umgebung

| Komponente | Empfehlung                  |
| ---------- | --------------------------- |
| OS           | Windows 10 Pro              |
| GPU         | 8 GB VRAM) |
| RAM        | 32 GB                       |
| Python     | 3.11                        |
| CUDA       | 12.9                        |
| Modell     | `DeepSeek-R1-0528-Qwen3-8B-GGUF` via Ollama     |

---

👉 [Komplette Dokumentation -  ]

---

## 📁 Projektstruktur

```
ace-data_tool/
├── webui/         → Gradio Interface
├── scripts/       → Lyrics, BPM, Tagging
├── include/       → Presets, Metadata, Prompt-Tools
├── presets/       → Stilvorgaben für Genres & Moods
├── config/        → Modell & API-Einstellungen
└── data/          → Deine Musik + generierte Dateien
```

---

## 🧩 Kompatibel mit:

* ✅ [ACE-Step Modell](https://github.com/ace-step/ACE-Step)
* ✅ [LoRA Training](.md)
* ✅ Lokale Ollama-Modelle (z. B. Qwen, DeepSeek, LLaMA2)

---

## 📜 Lizenz

Apache 2.0 – Feel free to fork, remix & contribute.
(c) 2025 by [`methmx83`](https://github.com/methmx83)

*🎶 Generieren Sie in Sekundenschnelle saubere, strukturierte Audio-Metadaten – vollautomatisch.*
