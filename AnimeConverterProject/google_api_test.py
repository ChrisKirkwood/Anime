import os
from google.cloud import translate_v2 as translate

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\Anime\credentials.json"

def translate_text(text):
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language="en")
    print(f"Translated Text: {result['translatedText']}")

if __name__ == "__main__":
    # Example text to translate
    text_to_translate = "こんにちは世界"  # "Hello, World" in Japanese
    translate_text(text_to_translate)
