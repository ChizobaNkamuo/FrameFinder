from frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber
from frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from frame_finder.pipeline.classes.pipeline import Pipeline
from frame_finder.pipeline.classes.local_data_store import LocalDataStore
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
from frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter

data_store = LocalDataStore()
username = "Chizoba"
video_id = "WorldModels"
load_video = True

speech_transcriber = WhisperTranscriber("small")
embedding_model = CLIPEmbeddingModel("openai/clip-vit-base-patch32")
query_classifier = RuleBasedClassifier()
query_rewriter = OllamaQueryRewriter("qwen2.5:1.5b")

pipeline = Pipeline(
    speech_transcriber, 
    embedding_model,
    query_classifier,
    query_rewriter
)

indexed_video = None

if load_video:
    indexed_video = data_store.load(username, video_id)
else:  
    transcripted_segments = pipeline.transcribe(f"sample_videos/{video_id}.mp4")["segments"]
    processed_segments = pipeline.process_segments(transcripted_segments)
    indexed_video = IndexedVideo(processed_segments,[])
    data_store.save(username, video_id, indexed_video)

formatted_query = pipeline.extract_query_info("Where is OpenAI mentioned?")
results = pipeline.search_for_query(formatted_query, indexed_video)