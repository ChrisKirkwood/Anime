from google.cloud import texttospeech, speech_v1p1beta1 as speech, translate_v2 as translate
import logging
import time
from audio_processing import split_audio_by_size  # Import the function

def transcribe_audio(audio_path, update_progress=None):
    client = speech.SpeechClient()
    audio_chunks = split_audio_by_size(audio_path)
    total_chunks = len(audio_chunks)

    transcripts = []
    for index, chunk in enumerate(audio_chunks):
        start_time = time.time()
        with open(chunk, 'rb') as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code="ja-JP"
        )

        logging.debug(f"Starting transcription for chunk {chunk} with config: {config}")
        try:
            response = client.recognize(config=config, audio=audio, timeout=300)  # Increased timeout
        except Exception as e:
            logging.error(f"Error transcribing chunk {chunk}: {e}")
            raise e

        duration = time.time() - start_time
        if duration > 60:
            logging.warning(f"Chunk {chunk} took too long to transcribe: {duration} seconds.")

        logging.info(f"Completed transcription for chunk {chunk}.")

        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)

        if update_progress:
            update_progress['value'] = int((index + 1) / total_chunks * 100)

    full_transcript = ' '.join(transcripts).strip()
    logging.info("Full transcription completed.")
    return full_transcript

def translate_text(text, update_progress=None):
    try:
        translate_client = translate.Client()
        logging.debug(f"Translating text with target language 'en': {text[:50]}...")
        result = translate_client.translate(text, target_language="en")
        translated_text = result['translatedText']
        logging.info("Text translation completed.")
        logging.info(f"Translated text: {translated_text[:50]}...")

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

        logging.debug(f"Starting speech synthesis with text: {text[:50]}...")
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
