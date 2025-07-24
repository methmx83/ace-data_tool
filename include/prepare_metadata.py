# prepare_metadata.py
import os
from audio_metadata_handler import AudioMetadataHandler

def prepare_all_metadata():
    """Bereitet Metadaten für alle Audio-Dateien im Projekt vor"""
    
    # Definiere Pfade relativ zum Skript
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # ACE DATA TOOL
    source_dir = os.path.join(base_dir, "data")
    
    # Unterstützte Audio-Formate
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.aac']
    
    # Finde alle Audio-Dateien
    audio_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(os.path.join(root, file))
    
    total_files = len(audio_files)
    if total_files == 0:
        print("Keine Audio-Dateien gefunden!")
        return
    
    print(f"Bereite Metadaten für {total_files} Audio-Dateien vor...")
    print("=" * 50)
    
    processed = 0
    errors = 0
    
    for i, audio_file in enumerate(audio_files, 1):
        try:
            rel_path = os.path.relpath(audio_file, source_dir)
            print(f"[{i}/{total_files}] {rel_path}")
            
            # Extrahiere und speichere Metadaten
            metadata = AudioMetadataHandler.extract_and_save_metadata(audio_file)
            
            if metadata:
                artist = metadata.get('artist', '')
                title = metadata.get('title', '')
                if artist or title:
                    print(f"  Tags: {artist} - {title}")
                else:
                    print(f"  Keine Tags gefunden, Dateiname verwendet")
                processed += 1
            else:
                print(f"  [FEHLER] Keine Metadaten extrahiert")
                errors += 1
                
        except Exception as e:
            print(f"  [FEHLER] {str(e)}")
            errors += 1
        
        print()
    
    # Zusammenfassung
    print("=" * 50)
    print("METADATEN-PREPARIERUNG ABGESCHLOSSEN")
    print("=" * 50)
    print(f"Erfolgreich verarbeitet: {processed} Dateien")
    print(f"Fehlerhaft: {errors} Dateien")
    print(f"Gesamt: {total_files} Dateien")
    print("=" * 50)

if __name__ == "__main__":
    prepare_all_metadata()