import os
import logging
import time
from google.cloud import texttospeech, speech_v1p1beta1 as speech, translate_v2 as translate
from anime_converter_utils import split_audio_by_size, extract_audio, convert_to_mono, merge_audio_video

# Set up Google Cloud credentials
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Anime/credentials.json"

# Setup logging
logging.basicConfig(
    filename='D:/Anime/log/backend.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def transcribe_audio(audio_path, update_progress=None):
    client = speech.SpeechClient()
    audio_chunks = split_audio_by_size(audio_path)
    total_chunks = len(audio_chunks)
    max_payload_size = 10485760  # 10 MB

    transcripts = []
    index = 0
    while index < len(audio_chunks):
        chunk = audio_chunks[index]
        start_time = time.time()

        # Check file size before transcribing
        while os.path.getsize(chunk) > max_payload_size:
            logging.warning(f"Chunk {chunk} exceeds 10 MB limit, splitting further.")
            sub_chunks = split_audio_by_size(chunk, max_size_bytes=max_payload_size)
            audio_chunks.extend(sub_chunks)
            audio_chunks.remove(chunk)
            chunk = sub_chunks[0]  # Proceed with the first sub-chunk

        with open(chunk, 'rb') as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code="ja-JP"
        )

        logging.debug(f"Starting transcription for chunk {chunk}")
        try:
            response = client.recognize(config=config, audio=audio, timeout=300)
            for result in response.results:
                transcripts.append(result.alternatives[0].transcript)
        except Exception as e:
            logging.error(f"Error transcribing chunk {chunk}: {e}")
            raise e

        duration = time.time() - start_time
        logging.info(f"Completed transcription for chunk {chunk} in {duration:.2f} seconds")

        if update_progress:
            update_progress['value'] = int((index + 1) / total_chunks * 100)
        
        index += 1

    full_transcript = ' '.join(transcripts).strip()
    logging.info("Full transcription completed.")
    logging.debug(f"Full transcript: {full_transcript[:500]}...")  # Log the first 500 characters

    return full_transcript

def translate_text(text, update_progress=None):
    try:
        translate_client = translate.Client()
        logging.debug(f"Translating text with target language 'en': {text[:500]}...")  # Log the first 500 characters
        result = translate_client.translate(text, target_language="en")
        translated_text = result['translatedText']
        logging.info("Text translation completed.")
        logging.debug(f"Translated text: {translated_text[:500]}...")  # Log the first 500 characters

        if update_progress:
            update_progress['value'] = 100

        return translated_text
    except Exception as e:
        logging.error(f"Error translating text: {e}")
        raise e

def synthesize_speech(text, output_audio_path, update_progress=None):
    try:
        client = texttospeech.TextToSpeechClient()
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        logging.debug(f"Starting speech synthesis with text: {text[:500]}...")  # Log the first 500 characters
        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config,
            timeout=300  # Increased timeout
        )

        with open(output_audio_path, "wb") as out:
            out.write(response.audio_content)
        logging.info(f"Synthesized speech saved to {output_audio_path}")

        if update_progress:
            update_progress['value'] = 100

        return output_audio_path
    except Exception as e:
        logging.error(f"Error during speech synthesis: {e}")
        raise e

# Isolated testing functions
def test_transcription(audio_path):
    transcript = transcribe_audio(audio_path)
    print(f"Transcript:\n{transcript}")

def test_translation(text):
    translated_text = translate_text(text)
    print(f"Translated Text:\n{translated_text}")

def test_synthesis(text, output_path):
    synth_path = synthesize_speech(text, output_path)
    print(f"Audio saved at: {synth_path}")

def test_merging(video_path, audio_path, output_video_path):
    merge_audio_video(video_path, audio_path, output_video_path)
    print(f"Video saved at: {output_video_path}")
