from dataclasses import dataclass
import torch

@dataclass
class VideoFrame:
    timestamp: float
    embedding: torch.Tensor