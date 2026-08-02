from frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber
from frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from frame_finder.pipeline.classes.pipeline import Pipeline
from frame_finder.pipeline.classes.local_data_store import LocalDataStore
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
from frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter
from frame_finder.pipeline.classes.opencv_frame_processor import OpenCVFrameProcessor
from frame_finder.pipeline.classes.pytorch_embedding_ranker import PytorchEmbeddingRanker

data_store = LocalDataStore()
username = "Chizoba"
video_id = "WorldModels"
load_video = True

speech_transcriber = WhisperTranscriber("small")
embedding_model = CLIPEmbeddingModel("openai/clip-vit-base-patch32")
frame_processor = OpenCVFrameProcessor(embedding_model)
query_classifier = RuleBasedClassifier()
query_rewriter = OllamaQueryRewriter("qwen2.5:1.5b")
embedding_ranker = PytorchEmbeddingRanker()

pipeline = Pipeline(
    speech_transcriber, 
    embedding_model,
    query_classifier,
    query_rewriter,
    frame_processor,
    embedding_ranker
)

indexed_video = None
if load_video:
    indexed_video = data_store.load(username, video_id)
else:  
    video_path = f"sample_videos/{video_id}.mp4"
    #transcripted_segments = pipeline.transcribe(video_path)["segments"]
    processed_frames = pipeline.process_frames(video_path, 10)
    processed_segments = []#pipeline.process_segments(transcripted_segments)
    indexed_video = IndexedVideo(processed_segments, processed_frames)
    data_store.save(username, video_id, indexed_video)

formatted_query = pipeline.extract_query_info("Show me where there's a diagram")#Where is OpenAI mentioned?
print(formatted_query)
results = pipeline.get_ranked_video(formatted_query, indexed_video)