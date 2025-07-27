import os
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from collections import Counter

# NLTK Initialisierung
nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)
sia = SentimentIntensityAnalyzer()
STOPWORDS = set(stopwords.words('english'))

LYRICS_WORD_LIMIT = 300


def load_standard_tags():
    try:
        tags = {
            "genres": [],
            "moods": [],
            "instruments": [],
            "rap_styles": []
        }
        
        if not os.path.exists("include/Moods.md"):
            raise FileNotFoundError("Moods.md nicht gefunden")

        with open("include/Moods.md", 'r', encoding='utf-8') as f:
            content = f.read()
        
        categories = {
            "genres": r'## Genre Liste:(.*?)(?=## Mood Liste:)',
            "moods": r'## Mood Liste:(.*?)(?=## Instrument Liste:)',
            "instruments": r'## Instrument Liste:(.*?)(?=## Rap Styles Liste:)',
            "rap_styles": r'## Rap Styles Liste:(.*?)(?=```|$)'
        }
        
        for category, pattern in categories.items():
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section = match.group(1).strip()
                if ',' in section and '\n' not in section:
                    items = [item.strip() for item in section.split(',')]
                else:
                    items = re.findall(r'^[\-\*]\s*(.+)$|^(.+)$', section, re.MULTILINE)
                    items = [item[0] or item[1] for item in items if any(item)]
                
                tags[category] = [item.strip().lower() for item in items if item.strip()]
        
        print(f"✅ Moods.md geladen: {len(tags['genres'])} Genres, {len(tags['moods'])} Moods, "
              f"{len(tags['instruments'])} Instrumente, {len(tags['rap_styles'])} Rap-Styles")
        return tags
    
    except Exception as e:
        print(f"⚠️ Fehler beim Laden von Moods.md: {str(e)}")
        print("Verwende Standard-Tags als Fallback")
        return {
            "genres": ["hip-hop", "rap", "trap", "german rap", "underground rap", "old school rap", "boom bap", "lo-fi hip hop"],
            "moods": ["aggressive", "gangster", "street", "deep", "sad", "happy", "party", "chill"],
            "instruments": ["drums", "bass", "synthesizer", "arpeggiator", "piano", "guitar", "strings"],
            "rap_styles": ["gangsta rap", "battle rap", "storytelling rap", "double-time rap", "trap rap", "lyrical rap", "male-vocal", "female-vocal"]
        }


STANDARD_TAGS = load_standard_tags()
ALL_STANDARD_TAGS = set(tag for sublist in STANDARD_TAGS.values() for tag in sublist)


def extract_clean_tags(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'/\w+\s*', '', text)
    
    tags = re.findall(r'\b([a-z0-9][a-z0-9\s\-]{2,28}[a-z0-9])\b', text, re.IGNORECASE)
    
    clean_tags = []
    for tag in tags:
        tag = re.sub(r'\s+', '-', tag.strip().lower())
        if 3 <= len(tag) <= 30:
            clean_tags.append(tag)
    
    validated_tags = sorted(
        set(clean_tags),
        key=lambda x: (x not in ALL_STANDARD_TAGS, x)
    )[:15]
    
    return validated_tags


def analyze_lyrics(lyrics):
    if not lyrics or len(lyrics) < 20:
        return {}
    
    words = lyrics.split()[:LYRICS_WORD_LIMIT]
    shortened_lyrics = " ".join(words)
    
    sentiment = sia.polarity_scores(shortened_lyrics)
    
    words = [word for word in re.findall(r'\b\w{3,}\b', shortened_lyrics.lower()) 
             if word not in STOPWORDS]
    
    if not words:
        return {"sentiment": sentiment}
    
    top_words = Counter(words).most_common(5)
    keywords = [word for word, _ in top_words]
    
    rap_features = []
    if any(word in keywords for word in ["rap", "hiphop", "mc", "flow"]):
        if sum(len(word) > 6 for word in words) / len(words) > 0.3:
            rap_features.append("complex-wordplay")
        if any(word in words for word in ["flow", "rhyme", "verse", "bar"]):
            rap_features.append("lyrical-focus")
        if "diss" in " ".join(words):
            rap_features.append("diss-track")
    
    return {
        "sentiment": sentiment,
        "top_keywords": keywords,
        "rap_features": rap_features
    }
