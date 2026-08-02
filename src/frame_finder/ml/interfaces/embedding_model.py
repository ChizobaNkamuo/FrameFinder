from abc import ABC, abstractmethod
from PIL import Image
import torch

class EmbeddingModel(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> torch.Tensor:
        pass

    @abstractmethod
    def embed_image(self, image: Image.Image) -> torch.Tensor:
        pass
    