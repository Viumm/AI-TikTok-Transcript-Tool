import tkinter as tk
from tkinter import ttk
import yt_dlp
import openai
import tempfile
import os
import re
import customtkinter

# API KEY
openai.api_key = 'sk-XXXX'

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class TikTokDownloaderApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("TikTok Transcript Downloader")
        self.geometry(f"{800}x{400}")

        header_label = customtkinter.CTkLabel(self, text="TikTok Transcript Downloader", font=customtkinter.CTkFont(size=18, weight="bold"))
        header_label.pack(pady=10)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(padx=20, pady=10, fill="both", expand=True)

        self.download_tab = ttk.Frame(self.tabs)
        self.history_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.download_tab, text="Downloader")
        self.tabs.add(self.history_tab, text="History")

        self.link_entry = tk.Text(self.download_tab, height=5)
        self.link_entry.pack(pady=10, padx=20, fill="both", expand=True)

        self.download_button = customtkinter.CTkButton(self.download_tab, text="Download", command=self.download_tiktok)
        self.download_button.pack(pady=20)

        self.history_listbox = tk.Listbox(self.history_tab)
        self.history_listbox.pack(fill="both", expand=True)

    def download_tiktok(self):
        tiktok_links = self.link_entry.get("1.0", "end-1c").split('\n')

        for tiktok_url in tiktok_links:
            tiktok_url = tiktok_url.strip()
            if not tiktok_url:
                continue

            def get_video_title(url):
                with yt_dlp.YoutubeDL() as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    video_title = info_dict.get('title', None)
                return video_title

            video_title = get_video_title(tiktok_url)

            sanitized_video_title = re.sub(r'#\w+\s*', '', video_title) if video_title else 'my_tiktok'
            sanitized_video_title = re.sub(r'[\/:*?"<>|]', '_', sanitized_video_title)

            transcripts_dir = 'transcripts'
            work_dir = 'work'
            if not os.path.exists(transcripts_dir):
                os.makedirs(transcripts_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',
                }],
                'outtmpl': os.path.join(work_dir, f'{sanitized_video_title}.%(ext)s'),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([tiktok_url])

            mp3_file_path = os.path.join(work_dir, f'{sanitized_video_title}.mp3')
            with open(mp3_file_path, 'rb') as mp3_file:
                mp3_data = mp3_file.read()

            temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir=work_dir)
            temp_audio_file.write(mp3_data)
            temp_audio_file.close()

            audio_file = open(temp_audio_file.name, "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            audio_file.close()

            transcription = transcript.text
            transcript_file_path = os.path.join(transcripts_dir, f'{sanitized_video_title}.txt')

            with open(transcript_file_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(transcription)

            self.history_listbox.insert(tk.END, f"Downloaded: {sanitized_video_title}")
            self.history_listbox.yview(tk.END)

            print(f"Transcription saved as {transcript_file_path}")
            os.remove(mp3_file_path)
            os.remove(temp_audio_file.name)
            print(f"The temporary files for {sanitized_video_title} have been deleted")

if __name__ == "__main__":
    app = TikTokDownloaderApp()
    app.mainloop()
