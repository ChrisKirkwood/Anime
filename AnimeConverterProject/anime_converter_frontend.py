import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import anime_converter_backend  # Import the first backend file
import anime_converter_backend2  # Import the second backend file
import logging
import threading  # For threading the GUI
from ocr_subtitle_extractor import extract_subtitles_with_google_vision  # Import the updated OCR script

# Ensure GOOGLE_APPLICATION_CREDENTIALS is set
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/Anime/credentials.json"

# Setup logging
logging.basicConfig(
    filename='D:/Anime/log/frontend.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

STATE_FILE_PATH = "D:/Anime/state_tracker.json"

def load_state():
    if os.path.exists(STATE_FILE_PATH):
        with open(STATE_FILE_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE_PATH, 'w') as f:
        json.dump(state, f)

def reset_state():
    if os.path.exists(STATE_FILE_PATH):
        os.remove(STATE_FILE_PATH)

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

def update_progress_bar(progress_bar, status_label, status, progress=0):
    status_label.config(text=status)
    progress_bar['value'] = progress
    root.update_idletasks()

def start_conversion_thread():
    threading.Thread(target=start_conversion).start()

def start_conversion():
    try:
        video_path = japanese_file_path.get()
        output_dir = output_directory.get()
        output_name = output_filename.get()

        if not video_path:
            messagebox.showerror("Error", "Please select a Japanese video file.")
            return
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return
        if not output_name:
            messagebox.showerror("Error", "Please enter an output filename.")
            return

        if not output_name.lower().endswith(('.mp4', '.mkv', '.avi')):
            output_name += '.mp4'  # Default to .mp4 if no valid extension is provided

        state = load_state()

        # Step 1: Extract Audio
        if not state.get("audio_extracted", False):
            update_progress_bar(progress_bar_audio_extraction, status_label_audio_extraction, "Extracting audio...", 10)
            extracted_audio_path = anime_converter_backend.extract_audio(video_path)
            state["audio_extracted"] = True
            state["extracted_audio_path"] = extracted_audio_path
            save_state(state)
            update_progress_bar(progress_bar_audio_extraction, status_label_audio_extraction, "Audio extraction completed", 100)
        else:
            extracted_audio_path = state["extracted_audio_path"]

        # Step 2: Convert to Mono
        if not state.get("audio_converted_to_mono", False):
            mono_audio_path = os.path.splitext(extracted_audio_path)[0] + '_mono.wav'
            anime_converter_backend.convert_to_mono(extracted_audio_path, mono_audio_path)
            state["audio_converted_to_mono"] = True
            state["mono_audio_path"] = mono_audio_path
            save_state(state)
            update_progress_bar(progress_bar_audio_extraction, status_label_audio_extraction, "Converted to Mono", 100)
        else:
            mono_audio_path = state["mono_audio_path"]

        # Step 3: Chunk Audio
        if not state.get("audio_chunked", False):
            update_progress_bar(progress_bar_chunking, status_label_chunking, "Chunking audio...", 10)
            audio_chunks = anime_converter_backend.split_audio_by_size(mono_audio_path)
            state["audio_chunked"] = True
            state["audio_chunks"] = audio_chunks
            save_state(state)
            update_progress_bar(progress_bar_chunking, status_label_chunking, "Audio chunking completed", 100)
        else:
            audio_chunks = state["audio_chunks"]

        # Step 4: Transcribe Audio
        if not state.get("audio_transcribed", False):
            update_progress_bar(progress_bar_transcription, status_label_transcription, "Transcribing audio...", 10)
            transcript = anime_converter_backend2.transcribe_audio(mono_audio_path)
            state["audio_transcribed"] = True
            state["transcript"] = transcript
            save_state(state)
            update_progress_bar(progress_bar_transcription, status_label_transcription, "Audio transcription completed", 100)
        else:
            transcript = state["transcript"]

        # Step 5: Translate Text
        if not state.get("text_translated", False):
            update_progress_bar(progress_bar_translation, status_label_translation, "Translating text...", 10)
            translated_text = anime_converter_backend2.translate_text(transcript)
            state["text_translated"] = True
            state["translated_text"] = translated_text
            save_state(state)
            update_progress_bar(progress_bar_translation, status_label_translation, "Text translation completed", 100)
        else:
            translated_text = state["translated_text"]

        # Step 6: Synthesize Speech
        if not state.get("speech_synthesized", False):
            synthesized_audio_path = os.path.join(output_dir, 'synthesized_audio.wav')
            update_progress_bar(progress_bar_tts, status_label_tts, "Synthesizing speech...", 10)
            anime_converter_backend2.synthesize_speech(translated_text, synthesized_audio_path)
            state["speech_synthesized"] = True
            state["synthesized_audio_path"] = synthesized_audio_path
            save_state(state)
            update_progress_bar(progress_bar_tts, status_label_tts, "Speech synthesis completed", 100)
        else:
            synthesized_audio_path = state["synthesized_audio_path"]

        # Step 7: Merge Audio and Video
        if not state.get("audio_video_merged", False):
            update_progress_bar(progress_bar_merge, status_label_merge, "Merging audio and video...", 10)
            anime_converter_backend.merge_audio_video(video_path, synthesized_audio_path, os.path.join(output_dir, output_name))
            state["audio_video_merged"] = True
            save_state(state)
            update_progress_bar(progress_bar_merge, status_label_merge, "Merging audio and video completed", 100)

        messagebox.showinfo(
            "Success",
            f"Conversion completed successfully!\nOutput saved at:\n{os.path.join(output_dir, output_name)}"
        )
        reset_state()

    except Exception as e:
        logging.error(f"Error during conversion: {str(e)}")
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def start_ocr_thread():
    threading.Thread(target=run_ocr).start()

def run_ocr():
    video_path = japanese_file_path.get()

    if not video_path:
        messagebox.showerror("Error", "Please select a Japanese video file.")
        return

    subtitles = extract_subtitles_with_google_vision(video_path)
    if subtitles:
        messagebox.showinfo("OCR Complete", "Subtitles extracted successfully.")
        logging.info("Extracted Subtitles:")
        logging.info("\n".join(subtitles))
    else:
        messagebox.showinfo("OCR Complete", "No subtitles were found in the video.")

def main():
    global root, japanese_file_path, output_directory, output_filename
    global progress_bar_audio_extraction, progress_bar_chunking, progress_bar_transcription
    global progress_bar_translation, progress_bar_tts, progress_bar_merge
    global status_label_audio_extraction, status_label_chunking, status_label_transcription
    global status_label_translation, status_label_tts, status_label_merge

    root = tk.Tk()
    root.title("Anime Converter")

    # Window size and position
    root.geometry("800x1000")  # Increased window size for better spacing and visibility
    root.resizable(True, True)  # Allow the window to be resizable

    # Japanese Video File Selection
    japanese_file_path = tk.StringVar()
    tk.Label(root, text="Select Japanese Video File:").pack(pady=(10, 0))
    tk.Entry(root, textvariable=japanese_file_path, width=80).pack(padx=10)
    tk.Button(root, text="Browse", command=select_japanese_file).pack(pady=5)

    # Output Directory Selection
    output_directory = tk.StringVar(value="D:/Anime/output")
    tk.Label(root, text="Select Output Directory:").pack(pady=(10, 0))
    tk.Entry(root, textvariable=output_directory, width=80).pack(padx=10)
    tk.Button(root, text="Browse", command=select_output_directory).pack(pady=5)

    # Output Filename Entry
    output_filename = tk.StringVar()
    tk.Label(root, text="Enter Output Filename:").pack(pady=(10, 0))
    tk.Entry(root, textvariable=output_filename, width=80).pack(padx=10)

    # Progress Bars and Status Labels
    status_label_audio_extraction = tk.Label(root, text="Audio Extraction: Not Started")
    status_label_audio_extraction.pack(pady=(10, 0))
    progress_bar_audio_extraction = ttk.Progressbar(root, length=700, mode='determinate')
    progress_bar_audio_extraction.pack(pady=(5, 0))

    status_label_chunking = tk.Label(root, text="Chunking: Not Started")
    status_label_chunking.pack(pady=(10, 0))
    progress_bar_chunking = ttk.Progressbar(root, length=700, mode='determinate')
    progress_bar_chunking.pack(pady=(5, 0))

    status_label_transcription = tk.Label(root, text="Transcription: Not Started")
    status_label_transcription.pack(pady=(10, 0))
    progress_bar_transcription = ttk.Progressbar(root, length=700, mode='determinate')
    progress_bar_transcription.pack(pady=(5, 0))

    status_label_translation = tk.Label(root, text="Translation: Not Started")
    status_label_translation.pack(pady=(10, 0))
    progress_bar_translation = ttk.Progressbar(root, length=700, mode='determinate')
    progress_bar_translation.pack(pady=(5, 0))

    status_label_tts = tk.Label(root, text="Text-to-Speech Synthesis: Not Started")
    status_label_tts.pack(pady=(10, 0))
    progress_bar_tts = ttk.Progressbar(root, length=700, mode='determinate')
    progress_bar_tts.pack(pady=(5, 0))

    status_label_merge = tk.Label(root, text="Merging Audio and Video: Not Started")
    status_label_merge.pack(pady=(10, 0))
    progress_bar_merge = ttk.Progressbar(root, length=700, mode='determinate')
    progress_bar_merge.pack(pady=(5, 0))

    # Start Conversion Button
    start_button = tk.Button(root, text="Start Conversion", command=start_conversion_thread, bg="green", fg="white", width=25)
    start_button.pack(pady=20)  # Ensure that the button is visible and properly packed

    # OCR Button
    ocr_button = tk.Button(root, text="Extract Subtitles (OCR)", command=start_ocr_thread, bg="blue", fg="white", width=25)
    ocr_button.pack(pady=10)  # Positioning the OCR button below the Start Conversion button

    root.mainloop()

if __name__ == "__main__":
    main()
