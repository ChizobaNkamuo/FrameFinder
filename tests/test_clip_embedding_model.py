import pytest, torch, os
from PIL import Image
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import frame_finder.ml.classes.clip_embedding_model as cem
from frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
load_dotenv()

MODEL_NAME = "openai/clip-vit-base-patch32"


def create_fake_model_and_processor():
    fake_processor = MagicMock()

    fake_inputs = MagicMock()
    fake_inputs.to.return_value = fake_inputs
    fake_processor.return_value = fake_inputs

    fake_model = MagicMock()
    fake_model.to.return_value = fake_model

    return fake_processor, fake_model, fake_inputs


def create_embedding_model(fake_processor, fake_model):
    return patch.multiple(
        cem,
        CLIPProcessor=MagicMock(
            from_pretrained=MagicMock(return_value=fake_processor)
        ),
        CLIPModel=MagicMock(
            from_pretrained=MagicMock(return_value=fake_model)
        ),
    )


def create_model_with_mocks():
    fake_processor, fake_model, fake_inputs = create_fake_model_and_processor()

    processor_patch = patch.object(
        cem.CLIPProcessor,
        "from_pretrained",
        return_value=fake_processor,
    )

    model_patch = patch.object(
        cem.CLIPModel,
        "from_pretrained",
        return_value=fake_model,
    )

    return (
        fake_processor,
        fake_model,
        fake_inputs,
        processor_patch,
        model_patch,
    )


def test_constructor_loads_processor_and_model():

    (
        fake_processor,
        fake_model,
        _,
        processor_patch,
        model_patch,
    ) = create_model_with_mocks()
    hf_token = os.getenv("HF_TOKEN")

    with processor_patch as mock_processor, model_patch as mock_model:

        embedding_model = CLIPEmbeddingModel(
            MODEL_NAME,
            device="cpu",
        )

        mock_processor.assert_called_once_with(
            MODEL_NAME,
            token=hf_token,
        )

        mock_model.assert_called_once_with(
            MODEL_NAME,
            token=hf_token,
        )

        fake_model.to.assert_called_once_with("cpu")
        fake_model.eval.assert_called_once()

        assert embedding_model._processor is fake_processor
        assert embedding_model._model is fake_model


def test_constructor_raises_for_invalid_model():

    with patch.object(
        cem.CLIPProcessor,
        "from_pretrained",
        side_effect=Exception(),
    ):

        with pytest.raises(ValueError):
            CLIPEmbeddingModel(
                "invalid-model",
                device="cpu",
            )


def test_embed_text_calls_processor_and_model():

    (
        fake_processor,
        fake_model,
        fake_inputs,
        processor_patch,
        model_patch,
    ) = create_model_with_mocks()

    embedding = torch.randn(512)

    fake_output = MagicMock()
    fake_output.pooler_output.squeeze.return_value = embedding

    fake_model.get_text_features.return_value = fake_output

    with processor_patch, model_patch:

        model = CLIPEmbeddingModel(
            MODEL_NAME,
            device="cpu",
        )

        result = model.embed_text("hello world")

        fake_processor.assert_called_once_with(
            text=["hello world"],
            return_tensors="pt",
            padding=True,
            truncation=True,
        )

        fake_inputs.to.assert_called_once_with("cpu")

        fake_model.get_text_features.assert_called_once_with(
            **fake_inputs
        )

        assert result is embedding


def test_embed_image_calls_processor_and_model():

    (
        fake_processor,
        fake_model,
        fake_inputs,
        processor_patch,
        model_patch,
    ) = create_model_with_mocks()

    embedding = torch.randn(512)

    fake_output = MagicMock()
    fake_output.pooler_output.squeeze.return_value = embedding

    fake_model.get_image_features.return_value = fake_output

    image = Image.new("RGB", (32, 32))

    with processor_patch, model_patch:

        model = CLIPEmbeddingModel(
            MODEL_NAME,
            device="cpu",
        )

        result = model.embed_image(image)

        fake_processor.assert_called_once_with(
            images=image,
            return_tensors="pt",
        )

        fake_inputs.to.assert_called_once_with("cpu")

        fake_model.get_image_features.assert_called_once_with(
            **fake_inputs
        )

        assert result is embedding