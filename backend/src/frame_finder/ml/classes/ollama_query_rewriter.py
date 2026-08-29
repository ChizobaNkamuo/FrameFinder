from src.frame_finder.ml.interfaces.query_rewriter import QueryRewriter
from src.frame_finder.files import load_text
from dotenv import load_dotenv
import requests, os
load_dotenv()

class OllamaQueryRewriter(QueryRewriter):
    _SYSTEM_PROMPT = load_text("src.frame_finder.config", "slm_system_prompt.txt")
    _OLLAMA_URL = os.getenv("OLLAMA_URL")

    def __init__(self, model: str):
        self._model = model

    def rewrite(self, query: str) -> str:
        response = requests.post(
            f"{self._OLLAMA_URL}/api/generate",
            json={
                "model": self._model,
                "messages": [
                    {
                        "role": "system",
                        "content": self._SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                "stream": False,
                "options": {
                    "temperature": 0,
                },
            },
        )

        return response["message"]["content"]