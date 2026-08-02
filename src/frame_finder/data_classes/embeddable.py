from dataclasses import dataclass
import torch

@dataclass
class Embeddable:
    embedding: torch.Tensor