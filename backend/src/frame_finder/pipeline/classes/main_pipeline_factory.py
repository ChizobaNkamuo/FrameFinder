from src.frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
from src.frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter
from src.frame_finder.pipeline.classes.pytorch_embedding_ranker import PytorchEmbeddingRanker
from src.frame_finder.pipeline.classes.open_cv_thumbnail_generator import OpenCVThumbnailGenerator
from src.frame_finder.data.classes.supabase_data_store_factory import SupabaseDataStoreFactory
from src.frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from src.frame_finder.pipeline.classes.main_pipeline import MainPipeline

class MainPipelineFactory():
    def new(self) -> MainPipeline:
        print("started main constructor -> embedding model")
        embedding_model = CLIPEmbeddingModel(model="openai/clip-vit-base-patch32", device="cpu")
        print("started classifier")
        query_classifier = RuleBasedClassifier()
        print("started ollama")
        query_rewriter = OllamaQueryRewriter(model="qwen2.5:1.5b")
        print("started ranker")
        embedding_ranker = PytorchEmbeddingRanker()
        print("started data factory")
        data_store_factory = SupabaseDataStoreFactory()
        print("started thumbnail generator")
        thumbnail_generator = OpenCVThumbnailGenerator()
        print("done")
        return None#MainPipeline(
            #embedding_model=embedding_model,
            #query_classifier=query_classifier,
            #query_rewriter=query_rewriter,
            #embedding_ranker=embedding_ranker,
            #data_store=data_store_factory.new(),
            #thumbnail_generator=thumbnail_generator,
        #)
