from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np

class ThumbnailGenerator(ABC):
    @abstractmethod
    def generate_thumbnail(
        self, 
        video_path: Path
    ) -> np.ndarray:
        pass