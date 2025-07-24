import os
import subprocess
from tinytag import TinyTag
import wave
import struct

def read_mp3_tags(mp3_file):
    """Liest Tags aus MP3-Datei"""
    try:
        tag = TinyTag.get(mp3_file)
        return {
            'artist': tag.artist or '',
            'title': tag.title or '',
            'album': tag.album or '',
            'year': tag.year or '',
            'genre': tag.genre or '',
            'comment': tag.comment or ''
        }
    except Exception as e:
        print(f"Fehler beim Lesen von Tags aus {mp3_file}: {e}")
        return {}

def write_wav_tags(wav_file, tags):
    """Fügt RIFF INFO Tags zu WAV-Datei hinzu"""
    try:
        # Liste der möglichen INFO-Tags
        tag_mapping = {
            'artist': 'IART',  # Artist
            'title': 'INAM',   # Name/Title
            'album': 'IPRD',   # Product/Album
            'year': 'ICRD',    # Creation Date
            'genre': 'IGNR',   # Genre
            'comment': 'ICMT'  # Comment
        }
        
        # Erstelle INFO Chunk Daten
        info_chunks = []
        for key, value in tags.items():
            if value and key in tag_mapping:
                tag_id = tag_mapping[key]
                # Kodiere als UTF-8 und füge Null-Terminator hinzu
                encoded_value = value.encode('utf-8') + b'\x00'
                # Pad auf gerade Anzahl Bytes
                if len(encoded_value) % 2:
                    encoded_value += b'\x00'
                # Erstelle Chunk
                chunk_data = tag_id.encode('ascii') + encoded_value
                info_chunks.append(chunk_data)
        
        if not info_chunks:
            return True
            
        # Kombiniere alle INFO Chunks
        info_data = b''.join(info_chunks)
        # Füge LIST Chunk Header hinzu
        list_chunk = b'LIST' + struct.pack('<I', len(info_data) + 4) + b'INFO' + info_data
        
        # Pad auf gerade Anzahl Bytes
        if len(list_chunk) % 2:
            list_chunk += b'\x00'
        
        # Lese Original WAV-Datei
        with open(wav_file, 'rb') as f:
            wav_data = f.read()
        
        # Finde die Position nach dem fmt Chunk
        if wav_data[0:4] != b'RIFF' or wav_data[8:12] != b'WAVE':
            return False
            
        # Suchen Sie nach dem fmt Chunk
        pos = 12
        while pos < len(wav_data):
            chunk_id = wav_data[pos:pos+4]
            chunk_size = struct.unpack('<I', wav_data[pos+4:pos+8])[0]
            
            if chunk_id == b'data':
                # Fügen Sie den LIST Chunk vor dem data Chunk ein
                new_wav = wav_data[:pos] + list_chunk + wav_data[pos:]
                break
            
            # Zum nächsten Chunk springen
            pos += 8 + chunk_size
            # Pad auf gerade Anzahl Bytes
            if chunk_size % 2:
                pos += 1
        else:
            # Fügen Sie den LIST Chunk ans Ende
            new_wav = wav_data + list_chunk
        
        # Schreibe aktualisierte WAV-Datei
        with open(wav_file, 'wb') as f:
            f.write(new_wav)
            
        return True
    except Exception as e:
        print(f"Fehler beim Schreiben von Tags in {wav_file}: {e}")
        return False

def convert_mp3_to_wav_with_tags():
    """Konvertiert MP3 zu WAV und übernimmt Tags"""
    
    # Definiere Pfade relativ zum Skript
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # audio_tagger_pro
    
    source_dir = os.path.join(base_dir, "tools\convert_tools\inputs")
    dest_dir = os.path.join(base_dir, "tools\convert_tools", "outputs")
    
    # Erstelle Zielverzeichnis
    os.makedirs(dest_dir, exist_ok=True)
    
    # Zähle Dateien
    mp3_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    
    total_files = len(mp3_files)
    if total_files == 0:
        print("Keine MP3-Dateien gefunden!")
        return
    
    print(f"Konvertiere {total_files} MP3-Dateien zu WAV...")
    print("=" * 50)
    
    success_count = 0
    error_count = 0
    
    for i, mp3_file in enumerate(mp3_files, 1):
        try:
            # Berechne relativen Pfad
            rel_path = os.path.relpath(mp3_file, source_dir)
            wav_filename = os.path.splitext(rel_path)[0] + '.wav'
            wav_file = os.path.join(dest_dir, wav_filename)
            
            # Erstelle Zielordner
            os.makedirs(os.path.dirname(wav_file), exist_ok=True)
            
            # Lese Tags aus MP3
            tags = read_mp3_tags(mp3_file)
            print(f"[{i}/{total_files}] {rel_path}")
            
            # Konvertiere MP3 zu WAV
            cmd = [
                'ffmpeg', '-i', mp3_file,
                '-vn', '-ar', '44100', '-ac', '2',
                '-c:a', 'pcm_s16le',
                '-fflags', '+bitexact',  # Für konsistente WAV-Header
                '-y', wav_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Füge Tags zur WAV-Datei hinzu
                if write_wav_tags(wav_file, tags):
                    # Zeige übernommene Tags
                    tag_info = []
                    for key, value in tags.items():
                        if value:
                            tag_info.append(f"{key}: {value}")
                    
                    if tag_info:
                        print(f"  Tags übernommen: {', '.join(tag_info)}")
                    else:
                        print("  Keine Tags gefunden")
                    success_count += 1
                    print(f"  [ERFOLG] -> {wav_filename}")
                else:
                    print(f"  [FEHLER] Tags konnten nicht geschrieben werden")
                    error_count += 1
            else:
                print(f"  [FEHLER] FFmpeg Fehler")
                error_count += 1
                
        except Exception as e:
            print(f"  [FEHLER] {str(e)}")
            error_count += 1
        
        # Fortschrittsanzeige
        progress = (i / total_files) * 100
        print(f"  Fortschritt: {progress:.1f}%")
        print()
    
    # Zusammenfassung
    print("=" * 50)
    print("KONVERTIERUNG ABGESCHLOSSEN")
    print("=" * 50)
    print(f"Erfolgreich konvertiert: {success_count} Dateien")
    print(f"Fehlerhaft: {error_count} Dateien")
    print(f"Gesamt: {total_files} Dateien")
    print(f"Ausgabeverzeichnis: {dest_dir}")
    print("=" * 50)
    input("Drücke Enter zum Beenden...")

# Ausführung
if __name__ == "__main__":
    convert_mp3_to_wav_with_tags()