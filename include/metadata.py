import re
import unicodedata

def clean_filename(name):
    """Removes illegal filesystem characters"""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def clean_rap_metadata(text):
    """Enhanced cleaning for track numbers, brackets, and feat./ft. tags"""
    text = re.sub(r'^\d+\.\s*|\(.*?\)|\[.*?\]', '', text)
    text = re.sub(r'(?i)\s*(feat\..*|ft\..*|featuring.*)', '', text)
    return text.strip()


def normalize_feature_artists(artist):
    """Replace feat. indicators with 'and' for URL construction"""
    return re.sub(r'(?i)\s*feat\.?\s*', ' and ', artist)


def normalize_string(text):
    """Normalize to ASCII and hyphenate for URLs"""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'\s+', '-', text).strip('-')
    """Normalize to ASCII, ersetze alle Arten von Bindestrichen durch '-', und hyphenate für URLs"""
    # Ersetze Unicode-Bindestriche und ähnliche Zeichen durch '-'
    dash_chars = [
        '\u2010', # Hyphen
        '\u2011', # Non-breaking hyphen
        '\u2012', # Figure dash
        '\u2013', # En dash
        '\u2014', # Em dash
        '\u2015', # Horizontal bar
        '\u2212', # Minus sign
        '\u2043', # Hyphen bullet
        '\uFE58', # Small em dash
        '\uFE63', # Small hyphen-minus
        '\uFF0D', # Fullwidth hyphen-minus
    ]
    for dash in dash_chars:
        text = text.replace(dash, '-')
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'\s+', '-', text).strip('-')
