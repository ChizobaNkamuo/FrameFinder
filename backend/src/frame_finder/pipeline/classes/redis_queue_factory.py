from src.frame_finder.pipeline.classes.redis_queue import RedisQueue
from src.frame_finder.pipeline.interfaces.worker_queue import WorkerQueue
from src.frame_finder.pipeline.interfaces.worker_queue_factory import WorkerQueueFactory
from redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

class RedisQueueFactory(WorkerQueueFactory):
    def new(self) -> WorkerQueue:
        redis = Redis(
            host=os.getenv("REDIS_URL")
        )

        return RedisQueue(
            redis=redis,
        )
