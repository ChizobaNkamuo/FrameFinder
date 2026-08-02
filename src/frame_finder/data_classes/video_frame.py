from dataclasses import dataclass
from frame_finder.data_classes.embeddable import Embeddable
import torch

@dataclass
class VideoFrame(Embeddable):
    timestamp: float
    embedding: torch.Tensor