from src.frame_finder.pipeline.classes.worker_pipeline_factory import WorkerPipelineFactory
from src.frame_finder.pipeline.classes.worker_pipeline import WorkerPipeline
import runpod

_worker_pipeline: WorkerPipeline | None = None

def get_worker_pipeline() -> WorkerPipeline:
    global _worker_pipeline

    if _worker_pipeline is None:
        _worker_pipeline = WorkerPipelineFactory().new()

    return _worker_pipeline

def process_video_job(
    user_id: str,
    video_id: str,
) -> None:
    worker_pipeline = get_worker_pipeline()

    worker_pipeline.process_video(
        user_id,
        video_id,
    )

def handler(job):
    data = job["input"]

    return process_video_job(
        user_id=data["user_id"],
        video_id=data["video_id"],
    )


runpod.serverless.start({
    "handler": handler
})