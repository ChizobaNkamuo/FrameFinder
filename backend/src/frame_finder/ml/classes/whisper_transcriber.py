import whisper, torch
from backend.src.frame_finder.ml.interfaces.speech_transcriber import SpeechTranscriber
from pathlib import Path

class WhisperTranscriber(SpeechTranscriber):
    def __init__(self, model_size: str, device: str | None = None):
        device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        try:
            self._model = whisper.load_model(model_size, device=device)
        except Exception as e:
            raise ValueError(f"Invalid or unsupported model size: {model_size}") from e

    def transcribe(self, audio_path: Path) -> dict:
        return self._model.transcribe(str(audio_path))