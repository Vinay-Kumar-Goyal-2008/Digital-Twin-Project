from youtube_transcript_api import YouTubeTranscriptApi
import json

video_id = "j3mhkYbznBk"

api = YouTubeTranscriptApi()
transcript = api.fetch(video_id)

with open("segments.json", "w", encoding="utf-8") as f:
    json.dump(transcript.to_raw_data(), f, indent=2)

print("Saved segments.json")