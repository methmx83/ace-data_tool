## 🧭 Project Plan: Optimization of ACE-STEP Data-Tool

### 📌 Goal
The Data-Tool should become more user-friendly, robust, configurable, and maintainable – ready for long-term community use.

---

## ✅ Milestone 1: Code Cleanup & Bug Fixes (Base Quality)
🎯 Goal: Fix minor errors, inconsistent filenames, and bugs.

**ToDo:**
- [ ] `save_tags` writes `*_prompts.txt` → rename to `*_prompt.txt` (without "s")
- [ ] Clean up duplicate `normalize_string()` definition & faulty docstring block
- [ ] Centralize logging initialization (`logging.basicConfig()` in `app.py`)
- [ ] Expand `.gitignore` for `*.log`, `__pycache__/`, `.DS_Store`, `.ipynb_checkpoints`

🛠 Effort: very low  
🔥 Priority: high

---

## 🚀 Milestone 2: Improve Configurability
🎯 Goal: Make input/output folders and server parameters dynamic.

**ToDo:**
- [ ] Actively use `input_dir` from `config.json` in code (instead of fixed `"data/"`)
- [ ] Load export path in UI from `config.json` (default value)
- [ ] Make `--port`, `--server_name` and `--share` controllable via CLI arguments (using `argparse`)
- [ ] Suggestion: `--headless` mode (see Milestone 4)

🛠 Effort: medium  
🔥 Priority: very high (more flexibility for users)

---

## ✨ Milestone 3: UI & UX Improvements
🎯 Goal: Optimize user guidance, simplify inputs, refine interface.

**ToDo:**
- [ ] Progress display → Show number of files to be tagged
- [ ] Improve mood slider: Add scale with labels ("Sad", "Neutral", "Happy") directly on slider
- [ ] New "Lyrics Viewer" tab in WebUI → Display/edit lyrics
- [ ] Sort "Genre Presets" dropdown alphabetically and highlight "(optional)" entry

🛠 Effort: medium  
🔥 Priority: high

---

## 🧠 Milestone 4: Headless/Batch Mode
🎯 Goal: Enable automated tool usage without WebUI

**ToDo:**
- [ ] CLI mode `--headless`: Tags all files from `input_dir`, exports to `output_dir`
- [ ] Progress display via stdout (e.g. with `tqdm`)
- [ ] Save console log as `batch.log`
- [ ] Optional: `--no-lyrics` mode if song lyrics aren't needed

🛠 Effort: medium–high  
🔥 Priority: medium (for advanced users & automation)

---

## 🧼 Milestone 5: Cleanup Requirements & Dependencies
🎯 Goal: Lightweight, clean Python environment

**ToDo:**
- [ ] Remove unnecessary packages: `mutagen`, `matplotlib`, `lazy_loader`
- [ ] Optional: Replace `nltk` with more compact alternatives (e.g. `textblob`, custom stopwords)
- [ ] Include `resampy` directly in `requirements.txt` instead of runtime install

🛠 Effort: low  
🔥 Priority: medium

---

## ⚙️ Milestone 6: Community Release Preparation
🎯 Goal: Prepare project for community use on GitHub

**ToDo:**
- [ ] Update README (installation, UI explanation, presets, export, example image)
- [ ] Create CHANGELOG.md with v1.0 → v1.1 progress
- [ ] CONTRIBUTING.md for Pull Requests / Bug Reports
- [ ] Clean up preset example folder (keep only 1–2 examples)

🛠 Effort: medium  
🔥 Priority: high

---