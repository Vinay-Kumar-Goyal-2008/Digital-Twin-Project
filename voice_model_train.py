import json
import torch
import torchaudio.transforms as T
import soundfile as sf
from torch.utils.data import Dataset, DataLoader
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
from torch.optim import AdamW
import torch.nn.functional as F

REDUCTION_FACTOR = 2
FRAME_SIZE = 256
ALIGN = FRAME_SIZE * REDUCTION_FACTOR


class SpeechSegmentDataset(Dataset):
    def __init__(self, audio_path, transcript_json, processor, target_sr=16000):
        self.processor = processor
        self.target_sr = target_sr

        with open(transcript_json, "r", encoding="utf-8") as f:
            all_segments = json.load(f)

        data, sr = sf.read(audio_path)
        waveform = torch.tensor(data).float()

        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.T

        waveform = waveform.mean(dim=0, keepdim=True)

        if sr != target_sr:
            waveform = T.Resample(sr, target_sr)(waveform)

        self.waveform = waveform
        self.sr = target_sr

        # Pre-filter valid segments at init time
        self.segments = []
        skipped = 0
        for seg in all_segments:
            text = seg.get("text", "").strip()
            if not text or "[Music]" in text:
                skipped += 1
                continue

            start_idx = int(seg["start"] * target_sr)
            end_idx = int((seg["start"] + seg["duration"]) * target_sr)
            audio_len = end_idx - start_idx

            if audio_len < 8000:
                skipped += 1
                continue

            trim_len = (audio_len // ALIGN) * ALIGN
            if trim_len == 0:
                skipped += 1
                continue

            self.segments.append(seg)

        print(f"Valid segments: {len(self.segments)} | Skipped: {skipped}")

        if len(self.segments) == 0:
            raise RuntimeError("No valid segments found. Check your audio/transcript files.")

    def __len__(self):
        return len(self.segments)

    def __getitem__(self, idx):
        seg = self.segments[idx]
        text = seg["text"].strip()

        start_idx = int(seg["start"] * self.sr)
        end_idx = int((seg["start"] + seg["duration"]) * self.sr)

        audio = self.waveform[:, start_idx:end_idx].squeeze(0)
        audio = torch.nan_to_num(audio).float()

        trim_len = (audio.shape[0] // ALIGN) * ALIGN
        audio = audio[:trim_len]

        inputs = self.processor(
            text=text,
            audio_target=audio,
            sampling_rate=self.sr,
            return_tensors="pt"
        )

        input_ids = inputs["input_ids"].squeeze(0)
        labels = inputs["labels"].squeeze(0)

        raw_mask = inputs.get("attention_mask")
        if raw_mask is not None:
            attention_mask = raw_mask.squeeze(0).long()
        else:
            attention_mask = torch.ones(input_ids.shape[0], dtype=torch.long)

        # Ensure labels frames divisible by reduction factor
        if labels.shape[0] % REDUCTION_FACTOR != 0:
            pad_len = REDUCTION_FACTOR - (labels.shape[0] % REDUCTION_FACTOR)
            labels = F.pad(labels, (0, 0, 0, pad_len), value=-100)

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }


def collate_fn(batch):
    input_ids = torch.nn.utils.rnn.pad_sequence(
        [b["input_ids"] for b in batch],
        batch_first=True,
        padding_value=0
    )

    attention_mask = torch.nn.utils.rnn.pad_sequence(
        [b["attention_mask"] for b in batch],
        batch_first=True,
        padding_value=0
    ).long()

    labels = torch.nn.utils.rnn.pad_sequence(
        [b["labels"] for b in batch],
        batch_first=True,
        padding_value=-100
    )

    if labels.shape[1] % REDUCTION_FACTOR != 0:
        pad_len = REDUCTION_FACTOR - (labels.shape[1] % REDUCTION_FACTOR)
        labels = F.pad(labels, (0, 0, 0, pad_len), value=-100)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)

    for p in model.speecht5.encoder.parameters():
        p.requires_grad = False

    dataset = SpeechSegmentDataset(
        audio_path="dataset\\audio\\audio.wav",
        transcript_json="segments.json",
        processor=processor
    )

    print("Dataset size:", len(dataset))

    loader = DataLoader(
        dataset,
        batch_size=4,
        shuffle=True,
        collate_fn=collate_fn
    )

    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-5)

    speaker_embeddings = torch.zeros(1, 512).to(device)

    model.train()
    print("Training started...")

    for epoch in range(10):
        total_loss = 0

        for batch in loader:
            optimizer.zero_grad()

            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            batch_size = input_ids.shape[0]
            speaker_embed_batch = speaker_embeddings.expand(batch_size, -1)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                speaker_embeddings=speaker_embed_batch
            )

            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1} | Loss: {total_loss / len(loader):.4f}")

    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict()
    }, "speecht5_finetuned.pt")
    print("Saved: speecht5_finetuned.pt")