from src.frame_finder.data_classes.embeddable import Embeddable
from src.frame_finder.pipeline.interfaces.embedding_ranker import EmbeddingRanker
from typing import List
import torch.nn.functional as F
import torch

class PytorchEmbeddingRanker(EmbeddingRanker):
    def rank_embeddings(
        self,
        query_embedding: torch.Tensor,
        items: List[Embeddable],
    ) -> List[Embeddable]:
        similarities = []

        for segment in items:
            similarity = F.cosine_similarity(
                query_embedding,
                segment.embedding,
                dim=0
            )

            similarities.append((segment, similarity.item()))

        similarities.sort(
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            segment
            for segment, _ in similarities
        ]
