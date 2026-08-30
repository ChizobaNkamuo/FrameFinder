from src.frame_finder.pipeline.classes.open_cv_frame_processor import OpenCVFrameProcessor
from src.frame_finder.pipeline.classes.open_cv_thumbnail_generator import OpenCVThumbnailGenerator
from src.frame_finder.pipeline.classes.requests_file_downloader import RequestsFileDownloader
from src.frame_finder.data.classes.supabase_data_store_factory import SupabaseDataStoreFactory
from src.frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber
from src.frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from src.frame_finder.pipeline.classes.worker_pipeline import WorkerPipeline

class WorkerPipelineFactory():
    def new(self) -> WorkerPipeline:
        speech_transcriber = WhisperTranscriber(model_size="small")
        embedding_model = CLIPEmbeddingModel(model="openai/clip-vit-base-patch32")
        frame_processor = OpenCVFrameProcessor(embedding_model=embedding_model)
        data_store_factory = SupabaseDataStoreFactory()
        thumbnail_generator = OpenCVThumbnailGenerator()
        file_downloader = RequestsFileDownloader()

        return WorkerPipeline(
            speech_transcriber=speech_transcriber,
            embedding_model=embedding_model,
            frame_processor=frame_processor,
            data_store=data_store_factory.new(),
            thumbnail_generator=thumbnail_generator,
            file_downloader=file_downloader
        )
