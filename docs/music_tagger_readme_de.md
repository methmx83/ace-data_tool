### 🚀 Vollständige Zusammenfassung des Projekts: Automatisierter Musik-Tagger 🎵

#### 🔧 Kernfunktionalität
- **Automatische Tag-Generierung** für Musikdateien basierend auf:
  - Audiodatei-Metadaten (Artist, Titel, Album, Jahr)
  - Lyrics-Analyse (Schlüsselwörter, Sentiment, Rap-Merkmale)
  - Tempo-Erkennung (BPM)
- **Integration mit lokalem LLM** (Ollama mit DeepSeek-R1 Modell)
- **Ausgabe**: Generierte Tags im Format `tag1, tag2, tag3` in `_prompt.txt` Dateien

#### ✅ Aktueller Stand & Errungenschaften
1. **Stabile Verarbeitung**:
   - Erfolgsrate: 100% (14/14 Dateien im letzten Durchlauf)
   - Durchschnittliche Verarbeitungszeit: ~14 Sekunden pro Datei

2. **Optimierte Komponenten**:
   ```mermaid
   graph TD
   A[Audiodatei] --> B[Metadaten-Extraktion]
   A --> C[Lyrics-Analyse]
   A --> D[Tempo-Erkennung]
   B --> E[LLM-Anfrage]
   C --> E
   D --> E
   E --> F[Tag-Generierung]
   F --> G[_prompt.txt]
   ```

3. **Schlüsseltechnologien**:
   - **Python 3.11+**
   - **Ollama** (lokaler LLM-Server)
   - **DeepSeek-R1-0528-Qwen3-8B** Modell (~10.5GB VRAM)
   - Bibliotheken: `eyed3`, `librosa`, `nltk`, `requests`

#### ⚙️ Konfiguration (musst du anpassen)
```python
# Zentrale Einstellungen
INPUT_DIR = r"Z:\AI\projects\music_scrape\music"  # Ordner für Audio Dateien
MODEL_NAME = "deep-x1_q8:latest"                 # Ollama Modellname
OLLAMA_URL = "http://localhost:11434/api/generate"
```

#### 📂 Dateistruktur (Beispiel)
```
music/
├── 01. Songtitel.mp3
├── 01. Songtitel_lyrics.txt   # Manuell erstellt
└── 01. Songtitel_prompt.txt   # Auto-generiert (Output)
```

#### 💡 Wichtige Features
- **Intelligente Tag-Validierung**:
  - Priorisiert Tags aus `Moods.md`
  - Filtert irrelevante Begriffe
  - Konvertiert zu `lowercase-hyphenated-format`
  
- **Robuste Fehlerbehandlung**:
  - Automatische Retries bei API-Fehlern
  - Fallback auf Standard-Tags
  - Ausführliches Error-Logging

- **Ressourcenmanagement**:
  - VRAM-optimierte sequentielle Verarbeitung
  - Tempo-Erkennung mit reduzierter Audio-Länge
  - Librosa-Cache deaktiviert

#### 📈 Performance-Daten (vom letzten Durchlauf)
```plaintext
✅ Moods.md geladen: 268 Genres, 204 Moods, 276 Instrumente, 90 Rap-Styles
Verarbeite 14 Dateien sequentiell...
⏱️ Dauer: 195.70s | Durchsatz: 0.07 Dateien/Minute
```

#### 🔜 Potenzielle Erweiterungen
1. **Batch-Verarbeitung** bei mehr VRAM
2. **Automatische Lyrics-Extraktion** (mit Audiotranskription)
3. **Cover-Art Generierung** via Stable Diffusion
4. **Playlist-Erstellung** basierend auf Tag-Ähnlichkeiten
5. **GUI-Oberfläche** für einfachere Bedienung
