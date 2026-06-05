# videos=['j3mhkYbznBk','4eRCygdW--c','EKWGGDXe5MA','H9fjhQMsDW4','P1ww1IXRfTA','GNhlNSLQAFE']
    # "4eRCygdW--c",
    # "EKWGGDXe5MA",
    # "uY-u1qyRM5w",
    # "mcD-5UfY1g0",
    # "LPDP_8X5Hug",
    # "ZcpwnozMh2U",
    # "-UFr1X0prbo",
    # "uY-u1qyRM5w"
import os
from youtube_transcript_api import YouTubeTranscriptApi

video_ids = [
    "j3mhkYbznBk"
]

output_dir = "feynman_data/youtube_transcripts"
os.makedirs(output_dir, exist_ok=True)

ytt_api = YouTubeTranscriptApi()

all_texts = []

def get_transcript(video_id):
    transcript_list = ytt_api.list(video_id)

    try:
        transcript = transcript_list.find_transcript(['en'])
    except:
        try:
            transcript = transcript_list.find_transcript(['en-GB'])
        except:
            transcript = transcript_list.find_transcript(['hi', 'en'])  # fallback

    return transcript.fetch()


for vid in video_ids:
    try:
        print(f"Processing: {vid}")

        transcript = get_transcript(vid)
        text = " ".join([t.text for t in transcript])
        
        all_texts.append(text)

    except Exception as e:
        print(f"Failed {vid}: {e}")
        break

# combined corpus
with open(f"{output_dir}/speech_text.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_texts))

print("DONE")