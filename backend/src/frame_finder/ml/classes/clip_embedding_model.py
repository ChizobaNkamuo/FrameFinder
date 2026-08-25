from PIL import Image
from transformers import CLIPModel, CLIPProcessor
from src.frame_finder.ml.interfaces.embedding_model import EmbeddingModel
from dotenv import load_dotenv
import torch, os
load_dotenv()

class CLIPEmbeddingModel(EmbeddingModel):
    def __init__(self, model: str, device: str | None = None):
        self._device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        hf_token = os.getenv("HF_TOKEN")

        try:
            self._processor = CLIPProcessor.from_pretrained(model, token=hf_token)
            self._model = CLIPModel.from_pretrained(model, token=hf_token).to(self._device)
            self._model.eval()
        except Exception as e:
            raise ValueError(f"Invalid or unsupported model: {model}") from e

    @torch.no_grad()
    def embed_text(self, text: str) -> torch.Tensor:
        inputs = self._processor(
            text=[text],
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self._device)

        embedding = self._model.get_text_features(**inputs).pooler_output.squeeze(0)
        return embedding

    @torch.no_grad()
    def embed_image(self, image: Image.Image) -> torch.Tensor:
        inputs = self._processor(
            images=image,
            return_tensors="pt",
        ).to(self._device)

        embedding = self._model.get_image_features(**inputs).pooler_output.squeeze(0)

        return embedding