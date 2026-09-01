from src.frame_finder.pipeline.interfaces.worker_queue import WorkerQueue
from src.frame_finder.api.worker import process_video_job
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

    def enqueue(self, user_id: str, video_id: str) -> str:
        job = self._queue.enqueue(
            process_video_job,
            user_id,
            video_id,
        )
        return job.id