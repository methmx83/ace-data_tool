import os
import re
import time

import requests
from bs4 import BeautifulSoup
from tinytag import TinyTag
from tqdm import tqdm
import unicodedata
from urllib.parse import quote

from include.metadata import clean_rap_metadata, normalize_string

# Configuration
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}
REQUEST_DELAY = 1.5

def get_audio_metadata(file_path):
    """Read title, artist, album from any audio file using Tinytag (supports WAV, MP3, FLAC, etc.)"""
    try:
        tag = TinyTag.get(file_path)
        title = tag.title or 'Unbekannter Titel'
        artist = tag.artist or 'Unbekannter Künstler'
        album = tag.album or 'Unbekanntes Album'
        print(f"[Tinytag] Titel={title}, Künstler={artist}")  # Kürzere Ausgabe
        return {'title': title, 'artist': artist, 'album': album}
    except Exception as e:
        print(f"Fehler bei Metadaten: {e}")  # Kürzere Ausgabe
        return {'title': '', 'artist': '', 'album': ''}


def process_single_file(file_path):
    """Fetch and save lyrics for one audio file"""
    try:
        meta = get_audio_metadata(file_path)
        artist = meta['artist']
        title = meta['title']

        lyrics = get_lyrics(artist, title)
        base = os.path.splitext(os.path.basename(file_path))[0]
        out_path = os.path.join(os.path.dirname(file_path), f"{base}_lyrics.txt")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"Künstler: {artist}\nTitel: {title}\n\n")
            f.write(lyrics)
        return True
    except Exception as e:
        return False


def scrape_genius_lyrics(artist, title):
    """Try two URL patterns to fetch lyrics HTML"""
    clean_artist = clean_rap_metadata(artist)
    clean_title = clean_rap_metadata(title)
    # Two URL variants
    url1 = f"https://genius.com/{normalize_string(clean_artist)}-{normalize_string(clean_title)}-lyrics"
    url2 = f"https://genius.com/{normalize_string(clean_title)}-{normalize_string(clean_artist)}-lyrics"
    
    # Debugging-Ausgaben
    print(f"Generated URL1: {url1}")
    print(f"Generated URL2: {url2}")

    for url in (url1, url2):
        print(f"Trying URL: {url}")  # Kürzere Ausgabe
        resp = requests.get(url, headers=HEADERS)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            containers = soup.select("div[class*='Lyrics__Container']") or soup.find_all("div", {"data-lyrics-container": "true"})
            if containers:
                text = ''
                for c in containers:
                    for block in c.select(".ReferentFragmentdesktop__ClickTarget, .Label"):
                        block.decompose()
                    text += c.get_text(separator="\n", strip=True) + "\n\n"
                return text.replace("[", "\n[").replace("]", "]\n").strip()
    return ''


def genius_search_fallback(artist, title):
    """Fallback search via Genius search page"""
    query = quote(f"{artist} {title}")
    search_url = f"https://genius.com/search?q={query}"
    print(f"Searching Genius: {search_url}")  # Kürzere Ausgabe
    resp = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.select("a[href*='/lyrics']")
    for link in links:
        href = link['href']
        if artist.lower() in link.get_text(strip=True).lower():
            return scrape_genius_lyrics_from_url(href)
    return ''


def scrape_genius_lyrics_from_url(url):
    """Scrape lyrics from a discovered Genius URL"""
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    containers = soup.select("div[class*='Lyrics__Container']") or soup.find_all("div", {"data-lyrics-container": "true"})
    if containers:
        return "\n\n".join(c.get_text(separator="\n", strip=True) for c in containers)
    return ''


def get_lyrics(artist, title):
    print(f"Suche Lyrics für: {artist} - {title}")  # Kürzere Ausgabe
    lyrics = scrape_genius_lyrics(artist, title)
    if not lyrics:
        time.sleep(REQUEST_DELAY)
        lyrics = genius_search_fallback(artist, title)
    return lyrics or 'Lyrics not found'


def load_lyrics(file_path):
    """Load existing lyrics file if present"""
    base = os.path.splitext(file_path)[0]
    path = f"{base}_lyrics.txt"
    return open(path, 'r', encoding='utf-8').read() if os.path.exists(path) else ''


def fetch_and_save_lyrics(artist, title, output_path):
    """Orchestrate lyrics fetch + save to output_path"""
    lyrics = get_lyrics(artist, title)
    if not lyrics or lyrics.lower() == 'lyrics not found':
        return False
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(lyrics)
    return True
