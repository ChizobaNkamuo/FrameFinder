from abc import ABC, abstractmethod
from pathlib import Path

class SpeechTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: Path) -> dict:
        pass
