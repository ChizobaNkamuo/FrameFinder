from src.frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
from src.frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter
from src.frame_finder.pipeline.classes.open_cv_frame_processor import OpenCVFrameProcessor
from src.frame_finder.pipeline.classes.pytorch_embedding_ranker import PytorchEmbeddingRanker
from src.frame_finder.pipeline.classes.open_cv_thumbnail_generator import OpenCVThumbnailGenerator
from src.frame_finder.pipeline.classes.requests_file_downloader import RequestsFileDownloader
from src.frame_finder.data.classes.supabase_data_store_factory import SupabaseDataStoreFactory
from src.frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber
from src.frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from src.frame_finder.pipeline.classes.pipeline import Pipeline

class PipelineFactory():
    def new(self) -> Pipeline:
        speech_transcriber = WhisperTranscriber(model_size="small")
        embedding_model = CLIPEmbeddingModel(model="openai/clip-vit-base-patch32")
        frame_processor = OpenCVFrameProcessor(embedding_model=embedding_model)
        query_classifier = RuleBasedClassifier()
        query_rewriter = OllamaQueryRewriter(model="qwen2.5:1.5b")
        embedding_ranker = PytorchEmbeddingRanker()
        data_store_factory = SupabaseDataStoreFactory()
        thumbnail_generator = OpenCVThumbnailGenerator()
        file_downloader = RequestsFileDownloader()

        return Pipeline(
            speech_transcriber=speech_transcriber, 
            embedding_model=embedding_model,
            query_classifier=query_classifier,
            query_rewriter=query_rewriter,
            frame_processor=frame_processor,
            embedding_ranker=embedding_ranker,
            data_store=data_store_factory.new(),
            thumbnail_generator=thumbnail_generator,
            file_downloader=file_downloader
        )
