from unittest.mock import patch
from frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter
import frame_finder.ml.classes.ollama_query_rewriter as oqr

def test_constructor_stores_model_name():
    rewriter = OllamaQueryRewriter("qwen2.5:1.5b")

    assert rewriter._model_name == "qwen2.5:1.5b"


def test_rewrite_returns_chat_response():
    fake_response = {
        "message": {
            "content": "OpenAI"
        }
    }

    with patch.object(oqr, "chat", return_value=fake_response):
        rewriter = OllamaQueryRewriter("qwen2.5:1.5b")

        result = rewriter.rewrite("Where is OpenAI mentioned?")

        assert result == "OpenAI"


def test_rewrite_calls_chat_correctly():
    fake_response = {
        "message": {
            "content": "OpenAI"
        }
    }

    with patch.object(oqr, "chat", return_value=fake_response) as mock_chat:

        rewriter = OllamaQueryRewriter("qwen2.5:1.5b")

        rewriter.rewrite("Where is OpenAI mentioned?")

        mock_chat.assert_called_once_with(
            model="qwen2.5:1.5b",
            messages=[
                {
                    "role": "system",
                    "content": rewriter._SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": "Where is OpenAI mentioned?",
                },
            ],
            options={
                "temperature": 0,
            },
        )