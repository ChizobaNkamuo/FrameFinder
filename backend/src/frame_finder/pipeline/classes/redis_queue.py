from src.frame_finder.pipeline.interfaces.worker_queue import WorkerQueue
from typing import Any, Callable
from redis import Redis
from rq import Queue

class RedisQueue(WorkerQueue):
    def __init__(
        self,
        redis: Redis,
    ):
        self._queue = Queue(
            connection=redis,
            default_timeout=1800
        )

    def enqueue(
        self,
        function: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        job = self._queue.enqueue(
            function,
            *args,
            **kwargs,
        )

        return job.id