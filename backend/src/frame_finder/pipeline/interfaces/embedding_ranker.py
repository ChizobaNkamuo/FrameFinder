from abc import ABC, abstractmethod
from src.frame_finder.data_classes.embeddable import Embeddable
from typing import List
import torch

class EmbeddingRanker(ABC):
    @abstractmethod
    def rank_embeddings(
        self,
        query_embedding: torch.Tensor,
        items: List[Embeddable],
    ) -> List[Embeddable]:
        pass