import os

# Paths to the files that need to be modified
OCR_SCRIPT_PATH = "ocr_subtitle_extractor.py"
BACKEND_SCRIPT_PATH = "anime_converter_backend.py"
FRONTEND_SCRIPT_PATH = "anime_converter_frontend.py"

# Check if the OCR script already exists, if not create it
if not os.path.exists(OCR_SCRIPT_PATH):
    with open(OCR_SCRIPT_PATH, 'w') as ocr_file:
        ocr_content = '''
import cv2
import pytesseract
import logging

def extract_subtitles_from_video(video_path):
    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not video_capture.isOpened():
        logging.error("Error: Could not open video.")
        return []

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
            logging.info(f"Frame {frame_count}: {text.strip()}")

        frame_count += 1

    video_capture.release()
    return subtitles
        '''
        ocr_file.write(ocr_content)
    print(f"{OCR_SCRIPT_PATH} created successfully.")

# Update backend script with OCR integration
with open(BACKEND_SCRIPT_PATH, 'a') as backend_file:
    backend_content = '''
from ocr_subtitle_extractor import extract_subtitles_from_video

def process_video_with_ocr(video_path):
    logging.info(f"Starting OCR processing for video: {video_path}")
    subtitles = extract_subtitles_from_video(video_path)
    logging.info(f"OCR processing completed. Extracted subtitles: {len(subtitles)}")
    return subtitles
    '''
    backend_file.write(backend_content)
print(f"OCR integration added to {BACKEND_SCRIPT_PATH}.")

# Update frontend script with OCR button and logic
with open(FRONTEND_SCRIPT_PATH, 'r') as frontend_file:
    frontend_content = frontend_file.read()

# Add OCR GUI elements if not already present
if 'OCR Extraction' not in frontend_content:
    with open(FRONTEND_SCRIPT_PATH, 'w') as frontend_file:
        frontend_content = frontend_content.replace(
            'root.mainloop()',
            '''
    # OCR Extraction Button
    ocr_button = tk.Button(root, text="Extract Subtitles (OCR)", command=start_ocr_extraction, bg="blue", fg="white", width=25)
    ocr_button.pack(pady=10)

    root.mainloop()

def start_ocr_extraction():
    try:
        video_path = japanese_file_path.get()
        if not video_path:
            messagebox.showerror("Error", "Please select a Japanese video file.")
            return

        subtitles = anime_converter_backend.process_video_with_ocr(video_path)
        with open(os.path.join(output_directory.get(), "extracted_subtitles.txt"), "w") as f:
            f.write("\\n".join(subtitles))
        messagebox.showinfo("Success", "Subtitles extracted and saved successfully!")

    except Exception as e:
        logging.error(f"Error during OCR extraction: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
            '''
        )
        frontend_file.write(frontend_content)
    print(f"OCR button and logic added to {FRONTEND_SCRIPT_PATH}.")

# Ensure logging is configured properly
LOGGING_CONFIG = '''
import logging

logging.basicConfig(
    filename='D:/Anime/log/application.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
'''

with open('logging_config.py', 'w') as logging_config_file:
    logging_config_file.write(LOGGING_CONFIG)
print("Logging configuration added.")

print("Setup complete. Run `python main.py` to start the application.")
