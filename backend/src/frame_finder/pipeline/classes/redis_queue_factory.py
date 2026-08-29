from src.frame_finder.pipeline.classes.redis_queue import RedisQueue
from src.frame_finder.pipeline.interfaces.worker_queue import WorkerQueue
from src.frame_finder.pipeline.interfaces.worker_queue_factory import WorkerQueueFactory
from redis import Redis

class RedisQueueFactory(WorkerQueueFactory):
    def new(self) -> WorkerQueue:
        redis = Redis(
            host="localhost",
            port=6379,
        )

        return RedisQueue(
            redis=redis,
        )
