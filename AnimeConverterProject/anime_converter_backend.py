import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip  # For video and audio manipulation
from pydub import AudioSegment  # For audio processing
from anime_converter_backend2 import transcribe_audio, translate_text, synthesize_speech  # Backend processing functions
from anime_converter_utils import split_audio_by_size, extract_audio, convert_to_mono, merge_audio_video  # Utility functions
from ocr_subtitle_extractor import extract_subtitles_with_google_vision  # Import the updated function name

def process_video_with_ocr(video_path):
    logging.info(f"Starting OCR processing for video: {video_path}")
    subtitles = extract_subtitles_with_google_vision(video_path)
    logging.info(f"OCR processing completed. Extracted subtitles: {len(subtitles)}")
    return subtitles

# OCR processing function
def handle_ocr_and_synthesize(video_path, output_dir):
    subtitles = process_video_with_ocr(video_path)
    if subtitles:
        translated_subtitles = translate_text("\n".join(subtitles))
        synthesized_audio_path = os.path.join(output_dir, 'synthesized_subtitles_audio.wav')
        synthesize_speech(translated_subtitles, synthesized_audio_path)
        logging.info(f"Synthesized subtitles saved to {synthesized_audio_path}")
        return synthesized_audio_path
    else:
        logging.info("No subtitles found in the video.")
        return None

# Global variable to track if a process is already running
process_running = False

# Set up Google Cloud credentials
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Anime/credentials.json"

# Setup logging
logging.basicConfig(
    filename='D:/Anime/log/backend.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ensure_output_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

def split_audio_by_size(audio_path, max_size_bytes=10485760):
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    current_chunk = AudioSegment.empty()
    current_size = 0

    for i in range(len(audio)):
        current_frame = audio[i]
        current_chunk += current_frame
        current_size += len(current_frame.raw_data)

        if current_size >= max_size_bytes:
            chunk_path = f"{audio_path}_chunk_{len(chunks)}.wav"
            current_chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
            logging.info(f"Created chunk {chunk_path}")
            current_chunk = AudioSegment.empty()
            current_size = 0

    if current_size > 0:
        chunk_path = f"{audio_path}_chunk_{len(chunks)}.wav"
        current_chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
        logging.info(f"Created final chunk {chunk_path}")

    return chunks

def extract_audio(video_path):
    try:
        logging.info(f"Extracting audio from video: {video_path}")
        audio_output_path = os.path.splitext(video_path)[0] + '_extracted_audio.wav'
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_output_path)
        logging.info(f"Audio extracted to {audio_output_path}")
        return audio_output_path
    except Exception as e:
        logging.error(f"Failed to extract audio: {e}")
        raise e

def convert_to_mono(input_audio_path, output_audio_path):
    """Converts stereo audio to mono."""
    sound = AudioSegment.from_wav(input_audio_path)
    mono_sound = sound.set_channels(1)
    mono_sound.export(output_audio_path, format="wav")
    logging.info(f"Converted {input_audio_path} to mono and saved as {output_audio_path}")

def merge_audio_video(original_video_path, synthesized_audio_path, output_video_path, update_progress=None):
    try:
        logging.info("Starting audio and video merging...")
        video = VideoFileClip(original_video_path)
        audio = AudioFileClip(synthesized_audio_path)

        # Ensure that the audio and video durations match
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        elif audio.duration < video.duration:
            # Extend audio by adding silence to match the video's length
            silence_duration = video.duration - audio.duration
            silence = AudioSegment.silent(duration=silence_duration * 1000)  # silence in milliseconds
            extended_audio = AudioSegment.from_wav(synthesized_audio_path) + silence
            extended_audio.export(synthesized_audio_path, format="wav")
            audio = AudioFileClip(synthesized_audio_path)

        final_video = video.set_audio(audio)
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
        logging.info(f"Final video saved to {output_video_path}")

        if update_progress:
            update_progress['value'] = 100
    except Exception as e:
        logging.error(f"Error during merging: {e}")
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
