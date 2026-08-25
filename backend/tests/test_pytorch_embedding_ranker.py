from dataclasses import dataclass
from src.frame_finder.pipeline.classes.pytorch_embedding_ranker import PytorchEmbeddingRanker
from src.frame_finder.data_classes.embeddable import Embeddable
import torch


@dataclass
class DummyEmbeddable(Embeddable):
    embedding: torch.Tensor
    name: str


def create_item(name: str, embedding: list[float]) -> DummyEmbeddable:
    return DummyEmbeddable(
        name=name,
        embedding=torch.tensor(embedding, dtype=torch.float32),
    )


def test_rank_embeddings_returns_most_similar_first():

    ranker = PytorchEmbeddingRanker()

    query = torch.tensor([1.0, 0.0])

    items = [
        create_item("orthogonal", [0.0, 1.0]),
        create_item("identical", [1.0, 0.0]),
        create_item("diagonal", [1.0, 1.0]),
    ]

    ranked = ranker.rank_embeddings(query, items)

    assert [item.name for item in ranked] == [
        "identical",
        "diagonal",
        "orthogonal",
    ]


def test_rank_embeddings_returns_empty_list_for_empty_input():

    ranker = PytorchEmbeddingRanker()

    query = torch.tensor([1.0, 0.0])

    ranked = ranker.rank_embeddings(query, [])

    assert ranked == []


def test_rank_embeddings_single_item():

    ranker = PytorchEmbeddingRanker()

    item = create_item("only", [1.0, 0.0])

    ranked = ranker.rank_embeddings(
        torch.tensor([1.0, 0.0]),
        [item],
    )

    assert ranked == [item]


def test_rank_embeddings_preserves_objects():

    ranker = PytorchEmbeddingRanker()

    item = create_item("test", [1.0, 0.0])

    ranked = ranker.rank_embeddings(
        torch.tensor([1.0, 0.0]),
        [item],
    )

    assert ranked[0] is item


def test_rank_embeddings_sorts_descending_similarity():

    ranker = PytorchEmbeddingRanker()

    query = torch.tensor([1.0, 0.0])

    best = create_item("best", [1.0, 0.0])
    middle = create_item("middle", [0.5, 0.5])
    worst = create_item("worst", [-1.0, 0.0])

    ranked = ranker.rank_embeddings(
        query,
        [middle, worst, best],
    )

    assert ranked == [
        best,
        middle,
        worst,
    ]