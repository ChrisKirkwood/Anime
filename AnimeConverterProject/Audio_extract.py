import os
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip

def log_error(message):
    with open("D:\\Anime\\error_log.txt", "a") as log_file:
        log_file.write(message + "\n")

def extract_audio(file_path, output_dir):
    try:
        audio_output_path = os.path.join(output_dir, os.path.basename(file_path).replace('.mp4', '.wav').replace('.mkv', '.wav').replace('.avi', '.wav'))
        
        # Extract audio from video
        video = VideoFileClip(file_path)
        video.audio.write_audiofile(audio_output_path, codec='pcm_s16le')
        
        messagebox.showinfo("Success", f"Audio extracted and saved to {audio_output_path}")
    except Exception as e:
        log_error(str(e))
        messagebox.showerror("Error", "An error occurred during audio extraction. Check the error log for details.")

def select_video_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mkv;*.avi")])
    video_file_path.set(file_path)

def select_output_directory():
    directory = filedialog.askdirectory()
    output_directory.set(directory)

# Set up the GUI
root = tk.Tk()
root.title("Audio Extractor")

video_file_path = tk.StringVar()
output_directory = tk.StringVar()

tk.Label(root, text="Select Video File:").pack()
tk.Entry(root, textvariable=video_file_path).pack(fill=tk.X, padx=10)
tk.Button(root, text="Browse", command=select_video_file).pack(pady=5)

tk.Label(root, text="Select Output Directory:").pack()
tk.Entry(root, textvariable=output_directory).pack(fill=tk.X, padx=10)
tk.Button(root, text="Browse", command=select_output_directory).pack(pady=5)

tk.Button(root, text="Extract Audio", command=lambda: extract_audio(video_file_path.get(), output_directory.get())).pack(pady=20)

root.mainloop()
