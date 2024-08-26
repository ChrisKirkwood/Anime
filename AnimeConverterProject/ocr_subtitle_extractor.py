import os
import cv2
import numpy as np
import logging
import openai
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from google.cloud import vision, texttospeech
import threading
import subprocess

# Setup logging
logging.basicConfig(
    filename='D:/Anime/log/ocr_extractor.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up Google Cloud credentials
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Anime/credentials.json"

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def preprocess_frame(frame):
    """
    Preprocess the frame to filter out noise and improve OCR accuracy.
    - Convert to grayscale
    - Increase contrast
    - Apply thresholding
    """
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enhanced_frame = cv2.equalizeHist(gray_frame)
    _, thresholded_frame = cv2.threshold(enhanced_frame, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresholded_frame

def extract_subtitles_with_google_vision(video_path, progress_bar, status_label):
    # Initialize the Google Vision client
    vision_client = vision.ImageAnnotatorClient()

    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        logging.error("Error: Could not open video.")
        return []

    subtitles = []
    frame_count = 0
    previous_text = ""

    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Preprocess the frame
        processed_frame = preprocess_frame(frame)

        # Convert the frame to bytes for Google Vision API
        success, encoded_image = cv2.imencode('.jpg', processed_frame)
        if not success:
            logging.error(f"Error encoding frame {frame_count}.")
            continue

        image = vision.Image(content=encoded_image.tobytes())

        # Perform text detection using Google Vision API
        response = vision_client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            detected_text = texts[0].description.strip()
            if detected_text and detected_text != previous_text:
                subtitles.append(detected_text)
                logging.info(f"Frame {frame_count}: {detected_text}")
                previous_text = detected_text  # To prevent redundancy

        frame_count += 1

        # Update progress bar
        progress = (frame_count / total_frames) * 100
        progress_bar['value'] = progress
        status_label.config(text=f"Extracting Subtitles: {int(progress)}%")
        root.update_idletasks()

    video_capture.release()
    logging.info("Google Vision subtitle extraction completed.")
    return subtitles

def filter_non_english_text(text):
    """
    Filter out non-English characters from the detected text.
    """
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?. ,'-\n"
    return ''.join(c for c in text if c in allowed_chars)

def process_with_openai(text, progress_bar, status_label):
    """
    Process the extracted text with OpenAI to create a continuous, coherent subtitle.
    """
    try:
        logging.info("Starting processing of text with OpenAI.")
        status_label.config(text="Processing with OpenAI...")
        root.update_idletasks()

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please combine the following extracted text into a continuous, coherent paragraph:\n\n{text}\n\n"}
            ],
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7
        )
        combined_text = response.choices[0].message['content'].strip()

        logging.info("OpenAI processing completed.")
        progress_bar['value'] = 100
        status_label.config(text="OpenAI Processing Completed")
        root.update_idletasks()

        return combined_text
    except Exception as e:
        logging.error(f"Error processing text with OpenAI: {e}")
        raise e

def synthesize_speech(text, output_audio_path, progress_bar, status_label):
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

        logging.info("Starting speech synthesis of processed text.")
        status_label.config(text="Synthesizing Speech...")
        root.update_idletasks()

        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config,
            timeout=300  # Increased timeout
        )

        with open(output_audio_path, "wb") as out:
            out.write(response.audio_content)
        logging.info(f"Synthesized speech saved to {output_audio_path}")

        progress_bar['value'] = 100
        status_label.config(text="Speech Synthesis Completed")
        root.update_idletasks()

    except Exception as e:
        logging.error(f"Error during speech synthesis: {e}")
        raise e

def merge_audio_video(video_path, audio_path, output_path):
    """
    Merges the provided audio track with the video, replacing the original audio.
    :param video_path: Path to the original video file.
    :param audio_path: Path to the new audio file (WAV).
    :param output_path: Path where the output video will be saved.
    """
    try:
        # Command to merge video and audio using ffmpeg
        command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-i', video_path,  # Input video file
            '-i', audio_path,  # Input audio file
            '-c:v', 'copy',  # Copy the video stream (no re-encoding)
            '-map', '0:v:0',  # Use the first video stream from the first file
            '-map', '1:a:0',  # Use the first audio stream from the second file
            '-shortest',  # Ensure the output duration is the shortest of the inputs
            output_path  # Output file
        ]

        logging.info(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
        logging.info(f"Successfully merged audio and video. Output saved to {output_path}")
        messagebox.showinfo("Merge Complete", f"Video and audio merged successfully. Output saved at: {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error merging audio and video: {e}")
        messagebox.showerror("Error", f"An error occurred while merging audio and video: {e}")

def start_ocr_thread():
    threading.Thread(target=run_ocr).start()

def run_ocr():
    video_path = japanese_file_path.get()
    output_dir = output_directory.get()
    output_name = output_filename.get()

    if not video_path:
        messagebox.showerror("Error", "Please select a Japanese video file.")
        return

    if not output_dir:
        output_dir = "D:/Anime/output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not output_name:
        output_name = "synthesized_subtitles"
    
    output_audio_path = os.path.join(output_dir, output_name + ".wav")
    output_video_path = os.path.join(output_dir, output_name + ".mp4")

    update_progress_bar(progress_bar_ocr, status_label_ocr, "Extracting Subtitles...", 0)

    subtitles = extract_subtitles_with_google_vision(video_path, progress_bar_ocr, status_label_ocr)
    if subtitles:
        filtered_text = filter_non_english_text("\n".join(subtitles))
        combined_text = process_with_openai(filtered_text, progress_bar_openai, status_label_openai)
        synthesize_speech(combined_text, output_audio_path, progress_bar_synthesis, status_label_synthesis)

        # Merge the new audio with the original video
        merge_audio_video(video_path, output_audio_path, output_video_path)

        messagebox.showinfo("OCR and Synthesis Complete", f"Subtitles extracted, processed, synthesized, and merged successfully.\nOutput saved at: {output_video_path}")
    else:
        messagebox.showinfo("OCR Complete", "No subtitles were found in the video.")

def update_progress_bar(progress_bar, status_label, status, progress=0):
    status_label.config(text=status)
    progress_bar['value'] = progress
    root.update_idletasks()

def select_japanese_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Video files", "*.mp4 *.mkv *.avi")]
    )
    if file_path:
        japanese_file_path.set(file_path)
        logging.info(f"Selected Japanese video file: {file_path}")

def select_output_directory():
    directory = filedialog.askdirectory()
    if directory:
        output_directory.set(directory)
        logging.info(f"Selected output directory: {directory}")

def main():
    global root, japanese_file_path, output_directory, output_filename
    global progress_bar_ocr, progress_bar_openai, progress_bar_synthesis
    global status_label_ocr, status_label_openai, status_label_synthesis

    root = tk.Tk()
    root.title("Anime Converter")

    # Window size and position
    root.geometry("600x800")  # Adjust as needed
    root.resizable(True, True)

    # Japanese Video File Selection
    japanese_file_path = tk.StringVar()
    tk.Label(root, text="Select Japanese Video File:").pack(pady=(10, 0))
    tk.Entry(root, textvariable=japanese_file_path, width=50).pack(padx=10)
    tk.Button(root, text="Browse", command=select_japanese_file).pack(pady=5)

    # Output Directory Selection
    output_directory = tk.StringVar(value="D:/Anime/output")
    tk.Label(root, text="Select Output Directory:").pack(pady=(10, 0))
    tk.Entry(root, textvariable=output_directory, width=50).pack(padx=10)
    tk.Button(root, text="Browse", command=select_output_directory).pack(pady=5)

    # Output Filename Entry
    output_filename = tk.StringVar()
    tk.Label(root, text="Enter Output Filename (without extension):").pack(pady=(10, 0))
    tk.Entry(root, textvariable=output_filename, width=50).pack(padx=10)

    # Progress Bars and Status Labels
    status_label_ocr = tk.Label(root, text="OCR: Not Started")
    status_label_ocr.pack(pady=(10, 0))
    progress_bar_ocr = ttk.Progressbar(root, length=500, mode='determinate')
    progress_bar_ocr.pack(pady=(5, 0))

    status_label_openai = tk.Label(root, text="OpenAI Processing: Not Started")
    status_label_openai.pack(pady=(10, 0))
    progress_bar_openai = ttk.Progressbar(root, length=500, mode='determinate')
    progress_bar_openai.pack(pady=(5, 0))

    status_label_synthesis = tk.Label(root, text="Speech Synthesis: Not Started")
    status_label_synthesis.pack(pady=(10, 0))
    progress_bar_synthesis = ttk.Progressbar(root, length=500, mode='determinate')
    progress_bar_synthesis.pack(pady=(5, 0))

    # OCR Button
    ocr_button = tk.Button(root, text="Extract and Process Subtitles (OCR)", command=start_ocr_thread, bg="blue", fg="white", width=30)
    ocr_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
