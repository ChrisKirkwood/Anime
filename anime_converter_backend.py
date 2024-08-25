
from ocr_subtitle_extractor import extract_subtitles_from_video

def process_video_with_ocr(video_path):
    logging.info(f"Starting OCR processing for video: {video_path}")
    subtitles = extract_subtitles_from_video(video_path)
    logging.info(f"OCR processing completed. Extracted subtitles: {len(subtitles)}")
    return subtitles
    