import cv2
import pytesseract
from pytesseract import Output

def extract_subtitles_from_video(video_path):
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not video_capture.isOpened():
        print("Error: Could not open video.")
        return

    subtitles = []
    frame_count = 0

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Use Tesseract to do OCR on the frame
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(frame, config=custom_config)
        if text.strip():  # If there is text, add it to subtitles
            subtitles.append(text.strip())
            print(f"Frame {frame_count}: {text.strip()}")

        frame_count += 1

    video_capture.release()
    return subtitles

if __name__ == "__main__":
    video_path = "D:\Anime\AnimeVids\OP1085JSS.mp4"
    subtitles = extract_subtitles_from_video(video_path)
    print("Extracted Subtitles:")
    print("\n".join(subtitles))
