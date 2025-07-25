import requests

def test_ollama_api():
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])
        print("Verfügbare Modelle:", models)
    except requests.exceptions.RequestException as e:
        print("Fehler beim Abrufen der Modelle:", e)

test_ollama_api()