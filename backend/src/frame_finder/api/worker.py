from src.frame_finder.pipeline.classes.pipeline_factory import PipelineFactory
from src.frame_finder.pipeline.classes.pipeline import Pipeline

worker_pipeline = PipelineFactory().new()

def get_worker_pipeline() -> Pipeline:
    return worker_pipeline