from dataclasses import dataclass
import torch

@dataclass
class Query:
    intent: str
    classification: str
    embedding: torch.Tensor