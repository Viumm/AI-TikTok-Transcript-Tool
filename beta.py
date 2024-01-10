import yt_dlp
import openai
import tempfile
import shutil
import os
import requests
import re  

# API KEY
openai.api_key = 'sk-XXXX'

tiktok_url = 'https://www.tiktok.com/@storyfavorites/video/7288030347474816286?is_from_webapp=1&sender_device=pc'

def get_video_title(url):
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
    return video_title

video_title = get_video_title(tiktok_url)

sanitized_video_title = re.sub(r'#\w+\s*', '', video_title) if video_title else 'my_tiktok'
sanitized_video_title = re.sub(r'[\/:*?"<>|]', '_', sanitized_video_title)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '0',
    }],
    'outtmpl': f'{sanitized_video_title}.%(ext)s',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([tiktok_url])

mp3_file_path = f'{sanitized_video_title}.mp3'
with open(mp3_file_path, 'rb') as mp3_file:
    mp3_data = mp3_file.read()

temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
temp_audio_file.write(mp3_data)
temp_audio_file.close()

audio_file = open(temp_audio_file.name, "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
audio_file.close()

transcription = transcript.text
transcript_file_path = f'{sanitized_video_title}.txt'  # Rename transcript file

with open(transcript_file_path, 'w', encoding='utf-8') as txt_file:
    txt_file.write(transcription)

print(f"Transcription saved as {transcript_file_path}")
os.remove(mp3_file_path)
print(f"The MP3 file {mp3_file_path} has been deleted")
