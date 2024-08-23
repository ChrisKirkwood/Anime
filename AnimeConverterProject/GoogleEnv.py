if __name__ == "__main__":
    import threading
    import tkinter as tk

    def main():
        root = tk.Tk()
        progress_var = tk.IntVar()
        japanese_file_path = "D:/Anime/AnimeVids/OP1085J.mp4"
        english_file_path = "D:/Anime/AnimeVids/OP1085E.mp4"
        output_name = "processed_video"
        test_mode = False

        # Start the conversion process
        conversion_thread = threading.Thread(
            target=process_files,
            args=(japanese_file_path, english_file_path, output_name, progress_var, test_mode)
        )
        conversion_thread.start()
        root.mainloop()

    main()
