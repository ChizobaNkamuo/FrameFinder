from abc import ABC, abstractmethod

class SpeechTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> dict:
        pass
