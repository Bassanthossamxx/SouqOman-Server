import asyncio
from googletrans import Translator

translator = Translator()

def arabic_to_english(text: str) -> str:
    """Translate Arabic text into English using Google Translate."""
    try:
        result = translator.translate(text, src='ar', dest='en')
        # If result is a coroutine (async), run it synchronously
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)
        return result.text
    except Exception:
        # fallback: just return the Arabic text if API fails
        return text
