import os
import glob
from shared_logs import LOGS, log_message

    # Main message when loading the file
log_message("... Clean Lyrics Script loaded ✅")

def bereinige_datei(dateipfad):
    """
    Cleans a single file by removing everything before the first line that begins with '['.
    """
    try:
        log_message(f"⏳ Processing lyrics: {dateipfad}")
        with open(dateipfad, 'r', encoding='utf-8') as datei:
            zeilen = datei.readlines()

        print(f"📄 File contents before cleaning:\n{''.join(zeilen[:5])}...")

        # Find the index of the first line that starts with '['
        start_index = None
        for i, zeile in enumerate(zeilen):
            if zeile.strip().startswith('['):
                start_index = i
                break

        # If such a line is found, write the part starting at this index
        # Otherwise, skip the file (remain unchanged)
        if start_index is not None:
            bereinigte_zeilen = zeilen[start_index:]
            
            # Overwrite the original file with the cleaned content
            with open(dateipfad, 'w', encoding='utf-8') as datei:
                datei.writelines(bereinigte_zeilen)

            log_message(f"💾 Lyrics cleaned up: {dateipfad}")
            print(f"📝 File contents after cleanup:\n{''.join(bereinigte_zeilen[:5])}...")
        else:
            print(f"⚠️ Skipped (no '['-line found): {dateipfad}")

    except Exception as e:
        print(f"❌ Error processing {dateipfad}: {e}")

def main():
    """
    Main function: Searches recursively for *_lyrics.txt files and cleans them.
    """
    # Setze den Ordner, in dem gesucht werden soll
    start_ordner = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    log_message(f"🔍 Search folders for existing lyrics: {start_ordner}")

    # Rekursive Suche nach allen Dateien mit dem Namen *_lyrics.txt
    suchmuster = os.path.join(start_ordner, '**', '*_lyrics.txt')
    lyrics_dateien = glob.glob(suchmuster, recursive=True)

    if not lyrics_dateien:
        log_message("⚠️ No files found with the name '*_lyrics.txt'.")
        return

    log_message(f"📂 Found files: {len(lyrics_dateien)}")

    for dateipfad in lyrics_dateien:
        bereinige_datei(dateipfad)

    log_message("✅ Processing completed.")

if __name__ == "__main__":
    main()