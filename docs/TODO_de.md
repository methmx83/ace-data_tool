## 🧭 Projektplan: Optimierung ACE-STEP Data-Tool

### 📌 Ziel
Das Data-Tool soll benutzerfreundlicher, robuster, konfigurierbarer und besser wartbar werden – bereit für dauerhaften Community-Einsatz.

---

## ✅ Meilenstein 1: Codebereinigung & Fehlerfixes (Basis-Qualität)
🎯 Ziel: Kleinere Fehler beheben, inkonsistente Dateinamen und Bugs korrigieren.

**ToDo:**
- [ ] `save_tags` schreibt `*_prompts.txt` → in `*_prompt.txt` umbenennen (ohne „s“)
- [ ] `normalize_string()` doppelte Definition & fehlerhaften Docstringblock bereinigen
- [ ] Logging-Initialisierung zentralisieren (`logging.basicConfig()` in `app.py`)
- [ ] `.gitignore` ergänzen für `*.log`, `__pycache__/`, `.DS_Store`, `.ipynb_checkpoints`

🛠 Aufwand: sehr gering  
🔥 Priorität: hoch

---

## 🚀 Meilenstein 2: Konfigurierbarkeit verbessern
🎯 Ziel: Input-/Output-Ordner und Server-Parameter dynamisch machen.

**ToDo:**
- [ ] `input_dir` aus `config.json` im Code aktiv verwenden (anstatt fix `"data/"`)
- [ ] Exportpfad im UI aus `config.json` laden (Standardwert)
- [ ] `--port`, `--server_name` und `--share` per CLI-Argument steuerbar machen (via `argparse`)
- [ ] Vorschlag: `--headless` Modus (siehe Meilenstein 4)

🛠 Aufwand: mittel  
🔥 Priorität: sehr hoch (mehr Flexibilität für User)

---

## ✨ Meilenstein 3: UI- & UX-Verbesserungen
🎯 Ziel: Nutzerführung optimieren, Eingaben vereinfachen, Oberfläche verfeinern.

**ToDo:**
- [ ] Fortschrittsanzeige → Anzahl der zu taggenden Dateien anzeigen
- [ ] Mood-Slider verbessern: Skala mit Labels („Traurig“, „Neutral“, „Fröhlich“) direkt am Slider
- [ ] Neuer Reiter „Lyrics Viewer“ im WebUI → Lyrics anzeigen/bearbeiten
- [ ] Dropdown „Genre Presets“ alphabetisch sortieren und „(optional)“-Eintrag hervorheben

🛠 Aufwand: mittel  
🔥 Priorität: hoch

---

## 🧠 Meilenstein 4: Headless-/Batch-Modus
🎯 Ziel: Tool auch ohne WebUI automatisiert nutzbar machen

**ToDo:**
- [ ] CLI-Modus `--headless`: taggt alle Dateien aus `input_dir`, exportiert nach `output_dir`
- [ ] Fortschrittsanzeige über stdout (z. B. mit `tqdm`)
- [ ] Konsolen-Log speichern als `batch.log`
- [ ] Optional: `--no-lyrics` Modus, falls Songtexte nicht benötigt werden

🛠 Aufwand: mittel–hoch  
🔥 Priorität: mittel (für Fortgeschrittene & Automatisierung)

---

## 🧼 Meilenstein 5: Requirements & Abhängigkeiten aufräumen
🎯 Ziel: Leichtgewichtiges, sauberes Python-Environment

**ToDo:**
- [ ] Unnötige Packages entfernen: `mutagen`, `matplotlib`, `lazy_loader`
- [ ] Optional: `nltk` ersetzen durch kompaktere Alternativen (z. B. `textblob`, eigene Stopwords)
- [ ] `resampy` direkt in `requirements.txt` statt Laufzeit-Install

🛠 Aufwand: gering  
🔥 Priorität: mittel

---

## ⚙️ Meilenstein 6: Vorbereitung für Community-Release
🎯 Ziel: Projekt auf GitHub auf Community-Einsatz vorbereiten

**ToDo:**
- [ ] README aktualisieren (Installation, UI-Erklärung, Presets, Export, Beispielbild)
- [ ] CHANGELOG.md anlegen mit v1.0 → v1.1 Fortschritten
- [ ] CONTRIBUTING.md für Pull Requests / Bug Reports
- [ ] preset-Beispielordner aufräumen (nur 1–2 Beispiele drin lassen)

🛠 Aufwand: mittel  
🔥 Priorität: hoch

---
