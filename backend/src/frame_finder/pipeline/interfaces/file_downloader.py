from abc import ABC, abstractmethod
from pathlib import Path

class FileDownloader(ABC):
    @abstractmethod
    def download(
        self,
        url: str,
        destination: Path,
    ) -> None:
        pass