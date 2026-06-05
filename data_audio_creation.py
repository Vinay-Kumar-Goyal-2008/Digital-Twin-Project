import json
import os
from pydub import AudioSegment

AUDIO_FILE = "./dataset/audio/audio.webm"
TRANSCRIPT_FILE = "segments.json"

OUTPUT_DIR = "dataset/chunks"
METADATA_FILE = "dataset/metadata.txt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

audio = AudioSegment.from_file(AUDIO_FILE)

with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
    segments = json.load(f)

metadata_lines = []

for i, seg in enumerate(segments):
    text = seg["text"].strip()

    if not text:
        continue

    start_ms = int(seg["start"] * 1000)
    end_ms = int((seg["start"] + seg["duration"]) * 1000)

    chunk = audio[start_ms:end_ms]

    # Skip extremely short clips
    if len(chunk) < 500:
        continue

    chunk = chunk.set_frame_rate(16000)
    chunk = chunk.set_channels(1)

    filename = f"chunk_{i:06d}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)

    chunk.export(filepath, format="wav")

    metadata_lines.append(f"{filename}|{text}")

with open(METADATA_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(metadata_lines))

print(f"Created {len(metadata_lines)} training samples")