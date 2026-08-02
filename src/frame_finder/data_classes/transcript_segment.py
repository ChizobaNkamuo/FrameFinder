from dataclasses import dataclass
import numpy as np

@dataclass
class TranscriptSegment:
    text: str
    start: float
    end: float
    embedding: np.ndarray