from audio_processing import extract_audio, convert_to_mono, split_audio_by_size
from speech_translation import transcribe_audio, translate_text, synthesize_speech
from video_processing import merge_audio_video
from utils import ensure_output_directory
import os
import logging

def process_video(video_path, output_dir, output_filename,
                  update_progress_audio=None, update_progress_chunking=None,
                  update_progress_transcription=None, update_progress_translation=None,
                  update_progress_tts=None, update_progress_merge=None,
                  update_status_audio=None, update_status_chunking=None,
                  update_status_transcription=None, update_status_translation=None,
                  update_status_tts=None, update_status_merge=None):
    try:
        logging.info(f"Processing video: {video_path}")

        # Ensure output directory exists
        ensure_output_directory(output_dir)

        # Step 1: Extract Audio from Video
        if update_progress_audio:
            update_progress_audio['value'] = 10
        if update_status_audio:
            update_status_audio.config(text="Audio extraction in progress...")
        extracted_audio_path = extract_audio(video_path)
        
        # Convert extracted audio to mono
        mono_audio_path = os.path.splitext(extracted_audio_path)[0] + '_mono.wav'
        convert_to_mono(extracted_audio_path, mono_audio_path)
        
        if update_progress_audio:
            update_progress_audio['value'] = 100
        if update_status_audio:
            update_status_audio.config(text="Audio extraction completed")

        # Step 2: Chunk Audio
        if update_progress_chunking:
            update_progress_chunking['value'] = 10
        if update_status_chunking:
            update_status_chunking.config(text="Chunking audio...")
        audio_chunks = split_audio_by_size(mono_audio_path)
        if update_progress_chunking:
            update_progress_chunking['value'] = 100
        if update_status_chunking:
            update_status_chunking.config(text="Audio chunking completed")

        # Step 3: Transcribe Audio to Text
        if update_progress_transcription:
            update_progress_transcription['value'] = 10
        if update_status_transcription:
            update_status_transcription.config(text="Transcribing audio...")
        transcript = transcribe_audio(mono_audio_path, update_progress=update_progress_transcription)
        if update_progress_transcription:
            update_progress_transcription['value'] = 100
        if update_status_transcription:
            update_status_transcription.config(text="Audio transcription completed")

        # Step 4: Translate Text to English
        if update_progress_translation:
            update_progress_translation['value'] = 10
        if update_status_translation:
            update_status_translation.config(text="Translating text...")
        translated_text = translate_text(transcript, update_progress=update_progress_translation)
        if update_progress_translation:
            update_progress_translation['value'] = 100
        if update_status_translation:
            update_status_translation.config(text="Text translation completed")

        # Step 5: Synthesize Speech from Translated Text
        synthesized_audio_path = os.path.join(output_dir, 'synthesized_audio.wav')
        if update_progress_tts:
            update_progress_tts['value'] = 10
        if update_status_tts:
            update_status_tts.config(text="Synthesizing speech...")
        synthesize_speech(translated_text, synthesized_audio_path, update_progress=update_progress_tts)
        if update_progress_tts:
            update_progress_tts['value'] = 100
        if update_status_tts:
            update_status_tts.config(text="Speech synthesis completed")

        # Step 6: Merge Synthesized Audio with Original Video
        if update_progress_merge:
            update_progress_merge['value'] = 10
        if update_status_merge:
            update_status_merge.config(text="Merging audio and video...")
        output_video_path = os.path.join(output_dir, output_filename)
        merge_audio_video(video_path, synthesized_audio_path, output_video_path, update_progress=update_progress_merge)
        if update_progress_merge:
            update_progress_merge['value'] = 100
        if update_status_merge:
            update_status_merge.config(text="Merging audio and video completed")

        # Optional: Clean up intermediate files
        os.remove(extracted_audio_path)
        os.remove(mono_audio_path)
        os.remove(synthesized_audio_path)

        logging.info(f"Processing completed successfully for video: {video_path}")
    except Exception as e:
        logging.error(f"Error processing video {video_path}: {str(e)}")
        raise e
