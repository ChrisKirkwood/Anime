from moviepy.editor import VideoFileClip, AudioFileClip
import logging

def merge_audio_video(original_video_path, synthesized_audio_path, output_video_path, update_progress=None):
    try:
        logging.info("Starting audio and video merging...")
        video = VideoFileClip(original_video_path)
        audio = AudioFileClip(synthesized_audio_path)

        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        elif audio.duration < video.duration:
            silence = AudioFileClip(synthesized_audio_path).subclip(0, video.duration - audio.duration)
            audio = audio.concatenate_videoclips([audio, silence])

        final_video = video.set_audio(audio)
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
        logging.info(f"Final video saved to {output_video_path}")

        if update_progress:
            update_progress['value'] = 100
    except Exception as e:
        logging.error(f"Error during merging: {e}")
        raise e
