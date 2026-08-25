from ollama import chat
from src.frame_finder.ml.interfaces.query_rewriter import QueryRewriter
from src.frame_finder.files import load_text

class OllamaQueryRewriter(QueryRewriter):
    _SYSTEM_PROMPT = load_text("src.frame_finder.config", "slm_system_prompt.txt")

    def __init__(self, model: str):
        self._model = model

    def rewrite(self, query: str) -> str:
        response = chat(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": self._SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": query,
                },
            ],
            options={
                "temperature": 0,
            },
        )

        return response["message"]["content"]