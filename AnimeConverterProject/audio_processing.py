from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import os
import logging

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
