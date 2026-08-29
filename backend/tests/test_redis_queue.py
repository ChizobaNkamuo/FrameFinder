from unittest.mock import MagicMock, patch
from src.frame_finder.pipeline.classes.redis_queue import RedisQueue
from redis import Redis

@patch(
    "src.frame_finder.pipeline.classes.redis_queue.Queue"
)
def test_enqueue_returns_job_id(mock_queue_class):
    redis = MagicMock(spec=Redis)

    mock_queue = mock_queue_class.return_value

    mock_job = MagicMock()
    mock_job.id = "job-123"

    mock_queue.enqueue.return_value = mock_job

    queue = RedisQueue(redis)

    def process_video(user_id: str, video_id: str):
        pass

    result = queue.enqueue(
        process_video,
        "user-1",
        "video-1",
    )

    assert result == "job-123"


@patch(
    "src.frame_finder.pipeline.classes.redis_queue.Queue"
)
def test_enqueue_passes_function_and_arguments(
    mock_queue_class,
):
    redis = MagicMock(spec=Redis)

    mock_queue = mock_queue_class.return_value

    mock_job = MagicMock()
    mock_job.id = "job-456"

    mock_queue.enqueue.return_value = mock_job

    queue = RedisQueue(redis)

    def process_video(user_id: str, video_id: str):
        pass

    queue.enqueue(
        process_video,
        "user-1",
        "video-1",
    )

    mock_queue.enqueue.assert_called_once_with(
        process_video,
        "user-1",
        "video-1",
    )


@patch(
    "src.frame_finder.pipeline.classes.redis_queue.Queue"
)
def test_enqueue_passes_keyword_arguments(
    mock_queue_class,
):
    redis = MagicMock(spec=Redis)

    mock_queue = mock_queue_class.return_value

    mock_job = MagicMock()
    mock_job.id = "job-789"

    mock_queue.enqueue.return_value = mock_job

    queue = RedisQueue(redis)

    def process_video(
        user_id: str,
        video_id: str,
        priority: int,
    ):
        pass

    queue.enqueue(
        process_video,
        "user-1",
        "video-1",
        priority=5,
    )

    mock_queue.enqueue.assert_called_once_with(
        process_video,
        "user-1",
        "video-1",
        priority=5,
    )


@patch(
    "src.frame_finder.pipeline.classes.redis_queue.Queue"
)
def test_queue_is_created_with_redis_connection(
    mock_queue_class,
):
    redis = MagicMock(spec=Redis)

    RedisQueue(redis)

    mock_queue_class.assert_called_once_with(
        connection=redis,
    )