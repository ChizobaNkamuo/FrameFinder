from abc import ABC, abstractmethod
from typing import Any, Callable

class WorkerQueue(ABC):
    @abstractmethod
    def enqueue(
        self,
        function: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        pass