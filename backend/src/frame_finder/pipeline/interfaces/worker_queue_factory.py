from src.frame_finder.pipeline.interfaces.worker_queue import WorkerQueue
from abc import ABC, abstractmethod

class WorkerQueueFactory(ABC):
    @abstractmethod
    def new(self) -> WorkerQueue:
        pass
