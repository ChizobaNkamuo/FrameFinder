from abc import ABC, abstractmethod

class WorkerQueue(ABC):
    @abstractmethod
    def enqueue(
        self,
        user_id: str,
        video_id: str,
    ) -> str:
        pass