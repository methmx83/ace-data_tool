# audio_metadata_handler.py
import os
import json
from tinytag import TinyTag

class AudioMetadataHandler:
    """Handler für Audio-Metadaten, auch für WAV-Dateien"""
    
    @staticmethod
    def extract_and_save_metadata(audio_file, metadata_file=None):
        """
        Extrahiert Metadaten aus Audio-Datei und speichert sie in JSON-Datei
        """
        if metadata_file is None:
            metadata_file = audio_file + ".metadata.json"
        
        try:
            # Lese Metadaten mit TinyTag
            tag = TinyTag.get(audio_file)
            
            # Erstelle Metadaten-Dictionary
            metadata = {
                'filename': os.path.basename(audio_file),
                'filepath': audio_file,
                'artist': tag.artist or '',
                'title': tag.title or '',
                'album': tag.album or '',
                'year': tag.year or '',
                'genre': tag.genre or '',
                'comment': tag.comment or '',
                'duration': tag.duration or 0,
                'filesize': os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
            }
            
            # Speichere Metadaten in JSON-Datei
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"Metadaten gespeichert: {metadata_file}")
            return metadata
            
        except Exception as e:
            print(f"Fehler beim Extrahieren von Metadaten aus {audio_file}: {e}")
            # Erstelle leere Metadaten-Datei als Fallback
            empty_metadata = {
                'filename': os.path.basename(audio_file),
                'filepath': audio_file,
                'artist': '',
                'title': os.path.splitext(os.path.basename(audio_file))[0],
                'album': '',
                'year': '',
                'genre': '',
                'comment': '',
                'duration': 0,
                'filesize': os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(empty_metadata, f, indent=2, ensure_ascii=False)
            
            return empty_metadata
    
    @staticmethod
    def load_metadata(audio_file):
        """
        Lädt Metadaten für Audio-Datei (aus JSON-Datei oder direkt)
        """
        metadata_file = audio_file + ".metadata.json"
        
        # Prüfe ob Metadaten-Datei existiert
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden von Metadaten-Datei {metadata_file}: {e}")
        
        # Fallback: Direktes Lesen mit TinyTag
        try:
            return AudioMetadataHandler.extract_and_save_metadata(audio_file, metadata_file)
        except Exception as e:
            print(f"Fehler beim Lesen von {audio_file}: {e}")
            return None
    
    @staticmethod
    def get_search_terms(audio_file):
        """
        Gibt Suchbegriffe für Lyrics-Suche zurück
        """
        metadata = AudioMetadataHandler.load_metadata(audio_file)
        
        if metadata:
            artist = metadata.get('artist', '').strip()
            title = metadata.get('title', '').strip()
            
            if artist and title:
                return f"{artist} {title}"
            elif title:
                return title
            else:
                # Fallback auf Dateinamen
                return os.path.splitext(os.path.basename(audio_file))[0]
        
        # Letzter Fallback
        return os.path.splitext(os.path.basename(audio_file))[0]

# Beispiel-Nutzung in deinem Hauptskript:
def example_usage():
    """Beispiel wie du es in deinem Lyrics-Skript nutzen kannst"""
    
    # Für jede Audiodatei:
    audio_files = [
        "dein_ordner/beispiel.wav",
        "dein_ordner/beispiel.mp3"
    ]
    
    for audio_file in audio_files:
        if os.path.exists(audio_file):
            # 1. Metadaten extrahieren und speichern (bei WAV)
            metadata = AudioMetadataHandler.extract_and_save_metadata(audio_file)
            
            # 2. Suchbegriffe für Genius.com erstellen
            search_term = AudioMetadataHandler.get_search_terms(audio_file)
            print(f"Suche Lyrics für: {search_term}")
            
            # 3. Hier kommt deine Genius.com Logik
            # fetch_lyrics_from_genius(search_term)

if __name__ == "__main__":
    example_usage()