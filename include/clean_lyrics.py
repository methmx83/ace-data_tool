import os
import glob

def bereinige_datei(dateipfad):
    """
    Bereinigt eine einzelne Datei, indem alles vor der ersten Zeile,
    die mit '[' beginnt, entfernt wird.
    """
    try:
        print(f"Verarbeite Datei: {dateipfad}")
        with open(dateipfad, 'r', encoding='utf-8') as datei:
            zeilen = datei.readlines()

        print(f"Datei-Inhalt vor Bereinigung:\n{''.join(zeilen[:5])}...")

        # Suche den Index der ersten Zeile, die mit '[' beginnt
        start_index = None
        for i, zeile in enumerate(zeilen):
            if zeile.strip().startswith('['):
                start_index = i
                break

        # Wenn eine solche Zeile gefunden wurde, schreibe den Teil ab diesem Index
        # Andernfalls überspringe die Datei (bleibt unverändert)
        if start_index is not None:
            bereinigte_zeilen = zeilen[start_index:]
            
            # Überschreibe die Originaldatei mit dem bereinigten Inhalt
            with open(dateipfad, 'w', encoding='utf-8') as datei:
                datei.writelines(bereinigte_zeilen)
            
            print(f"Bereinigt: {dateipfad}")
            print(f"Datei-Inhalt nach Bereinigung:\n{''.join(bereinigte_zeilen[:5])}...")
        else:
            print(f"Übersprungen (keine '['-Zeile gefunden): {dateipfad}")

    except Exception as e:
        print(f"Fehler beim Verarbeiten von {dateipfad}: {e}")

def main():
    """
    Hauptfunktion: Sucht rekursiv nach *_lyrics.txt Dateien und bereinigt sie.
    """
    # Setze den Ordner, in dem gesucht werden soll
    start_ordner = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    print(f"Durchsuche Ordner: {start_ordner}")

    # Rekursive Suche nach allen Dateien mit dem Namen *_lyrics.txt
    suchmuster = os.path.join(start_ordner, '**', '*_lyrics.txt')
    lyrics_dateien = glob.glob(suchmuster, recursive=True)

    if not lyrics_dateien:
        print("Keine Dateien mit dem Namen '*_lyrics.txt' gefunden.")
        return

    print(f"Gefundene Dateien: {len(lyrics_dateien)}")
    
    for dateipfad in lyrics_dateien:
        bereinige_datei(dateipfad)

    print("\nVerarbeitung abgeschlossen.")

if __name__ == "__main__":
    main()