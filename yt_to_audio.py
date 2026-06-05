import os
from yt_dlp import YoutubeDL

def extract_audio_from_youtube(youtube_url, output_dir="dataset/audio"):
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

if __name__ == "__main__":
    extract_audio_from_youtube(
        "https://www.youtube.com/watch?v=j3mhkYbznBk"
    )