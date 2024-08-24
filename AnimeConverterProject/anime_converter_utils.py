import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

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
