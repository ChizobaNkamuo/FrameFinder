from unittest.mock import MagicMock, patch
import pytest
import frame_finder.ml.classes.whisper_transcriber as wt
from frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber

VALID_MODELS = [
    "tiny",
    "base",
    "small",
    "medium",
    "large",
    "large-v2",
    "large-v3",
    "turbo",
]

@pytest.mark.parametrize("model_name", VALID_MODELS)
def test_constructor_loads_valid_model(model_name):
    with patch.object(wt.whisper, "load_model") as mock_load:
        fake_model = MagicMock()
        mock_load.return_value = fake_model

        device = "cpu"
        transcriber = WhisperTranscriber(model_name, device=device)

        mock_load.assert_called_once_with(model_name, device=device)
        assert transcriber._model is fake_model

def test_constructor_rejects_invalid_model():
    with pytest.raises(ValueError):
        WhisperTranscriber("")

def test_transcribe_delegates_to_whisper_model():
    fake_model = MagicMock()
    fake_model.transcribe.return_value = {
        "text": "Hello world"
    }
    
    with patch.object(wt.whisper, "load_model", return_value=fake_model):
        transcriber = WhisperTranscriber("base")

        result = transcriber.transcribe("audio.mp3")

        fake_model.transcribe.assert_called_once_with("audio.mp3")
        assert result == {"text": "Hello world"}