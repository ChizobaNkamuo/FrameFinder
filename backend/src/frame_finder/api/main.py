from fastapi import BackgroundTasks, FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from backend.src.frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber
from backend.src.frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from backend.src.frame_finder.pipeline.classes.pipeline import Pipeline
from backend.src.frame_finder.pipeline.classes.local_data_store import LocalDataStore
from backend.src.frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
from backend.src.frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter
from backend.src.frame_finder.pipeline.classes.open_cv_frame_processor import OpenCVFrameProcessor
from backend.src.frame_finder.pipeline.classes.pytorch_embedding_ranker import PytorchEmbeddingRanker
from backend.src.frame_finder.pipeline.classes.open_cv_thumbnail_generator import OpenCVThumbnailGenerator
from backend.src.frame_finder.pydantic_classes.light_video_response import LightVideoResponse
from backend.src.frame_finder.pydantic_classes.search_response import SearchResponse
from backend.src.frame_finder.pydantic_classes.video_frame import VideoFrame
from backend.src.frame_finder.pydantic_classes.transcript_segment import TranscriptSegment
import datetime

speech_transcriber = WhisperTranscriber(model_size="small")
embedding_model = CLIPEmbeddingModel(model="openai/clip-vit-base-patch32")
frame_processor = OpenCVFrameProcessor(embedding_model=embedding_model)
query_classifier = RuleBasedClassifier()
query_rewriter = OllamaQueryRewriter(model="qwen2.5:1.5b")
embedding_ranker = PytorchEmbeddingRanker()
data_store = LocalDataStore(root=Path("data"))
thumbnail_generator = OpenCVThumbnailGenerator()

pipeline = Pipeline(
    speech_transcriber=speech_transcriber, 
    embedding_model=embedding_model,
    query_classifier=query_classifier,
    query_rewriter=query_rewriter,
    frame_processor=frame_processor,
    embedding_ranker=embedding_ranker,
    data_store=data_store,
    thumbnail_generator=thumbnail_generator
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/index/upload/{username}")
async def upload_video(
    username: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> None:
    video_id = pipeline.generate_video_id()
    file_path = pipeline.save_upload(username, video_id, file,
            {
                "status": "processing",
                "stage": "Transcribing...",
                "created_at" : str(datetime.datetime.now())
            })
    thumbnail = pipeline.generate_thumbnail(file_path)
    pipeline.save_thumbnail(username, video_id, thumbnail)
    background_tasks.add_task(
        pipeline.index_video,
        username,
        video_id,
        file_path
    )

    return {"video_id": video_id}

@app.post("/search/{username}/{video_id}")
async def search(
    username: str,
    video_id: str,
    query: str,
    top_k: int = 10
):
    video_data = pipeline.load_video(username, video_id)
    formatted_query = pipeline.extract_query_info(query)
    ranked_video = pipeline.get_ranked_video(formatted_query, video_data.indexed_video, top_k)

    return SearchResponse(
            video_frames=[
                VideoFrame(
                    timestamp=int(video_frame.timestamp)
                ) 
                for video_frame in ranked_video.video_frames],

            transcript_segments=[
                TranscriptSegment(
                    timestamp=int(transcript_segment.start),
                    text=transcript_segment.text
                ) 
                for transcript_segment in ranked_video.transcript_segments]
        )

@app.get("/videos/{username}", response_model=list[LightVideoResponse])
async def get_all_videos(username: str):
    videos = pipeline.load_all(username)

    return [
        LightVideoResponse(
            video_id=video.metadata["video_id"],
            filename=video.metadata["filename"],
            thumbnail_url=f"/videos/{username}/{video.metadata["video_id"]}/thumbnail",
            status=video.metadata["status"],
            stage=video.metadata["stage"],
            created_at=video.metadata["created_at"],
        )
        for video in videos
    ]

@app.get("/videos/{username}/{video_id}/thumbnail")
async def get_thumbnail(username: str, video_id: str):
    video = pipeline.load_video(username, video_id)

    return FileResponse(
        video.thumbnail_path,
        media_type="image/jpeg",
    )

@app.get("/videos/{username}/{video_id}/file")
def get_video_file(username: str, video_id: str):
    video = pipeline.load_video(username, video_id)

    return FileResponse(
        video.video_path,
        media_type="video/mp4"
    )

print("start")
#pipeline.index_video("Chizoba", Path("sample_videos") / "WorldModels.mp4")
print("done")