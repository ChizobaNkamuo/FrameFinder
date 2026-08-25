from dataclasses import dataclass
from src.frame_finder.data_classes.embeddable import Embeddable
import numpy as np

@dataclass
class TranscriptSegment(Embeddable):
    text: str
    start: float
    end: float
    embedding: np.ndarray