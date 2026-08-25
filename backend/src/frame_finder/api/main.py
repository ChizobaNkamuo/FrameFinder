from fastapi import BackgroundTasks, FastAPI, UploadFile, File, HTTPException, Depends
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from src.frame_finder.ml.classes.whisper_transcriber import WhisperTranscriber
from src.frame_finder.ml.classes.clip_embedding_model import CLIPEmbeddingModel
from src.frame_finder.pipeline.classes.pipeline import Pipeline

from src.frame_finder.pipeline.classes.rule_based_classifier import RuleBasedClassifier
from src.frame_finder.ml.classes.ollama_query_rewriter import OllamaQueryRewriter
from src.frame_finder.pipeline.classes.open_cv_frame_processor import OpenCVFrameProcessor
from src.frame_finder.pipeline.classes.pytorch_embedding_ranker import PytorchEmbeddingRanker
from src.frame_finder.pipeline.classes.open_cv_thumbnail_generator import OpenCVThumbnailGenerator
from src.frame_finder.pipeline.classes.temporary_storage import TemporaryStorage
from src.frame_finder.data.classes.supabase_auth_provider_factory import SupabaseAuthProviderFactory
from src.frame_finder.data.classes.supabase_data_store_factory import SupabaseDataStoreFactory
from src.frame_finder.pydantic_classes.light_video_response import LightVideoResponse
from src.frame_finder.pydantic_classes.search_response import SearchResponse
from src.frame_finder.pydantic_classes.video_frame import VideoFrame
from src.frame_finder.pydantic_classes.transcript_segment import TranscriptSegment
from src.frame_finder.pydantic_classes.auth_response import AuthResponse
from src.frame_finder.pydantic_classes.user import User

import datetime

speech_transcriber = WhisperTranscriber(model_size="small")
embedding_model = CLIPEmbeddingModel(model="openai/clip-vit-base-patch32")
frame_processor = OpenCVFrameProcessor(embedding_model=embedding_model)
query_classifier = RuleBasedClassifier()
query_rewriter = OllamaQueryRewriter(model="qwen2.5:1.5b")
embedding_ranker = PytorchEmbeddingRanker()
data_store_factory = SupabaseDataStoreFactory()
thumbnail_generator = OpenCVThumbnailGenerator()
auth_provider_factory = SupabaseAuthProviderFactory()
auth_provider = auth_provider_factory.new()
temporary_storage = TemporaryStorage(root=Path("temp"))

pipeline = Pipeline(
    speech_transcriber=speech_transcriber, 
    embedding_model=embedding_model,
    query_classifier=query_classifier,
    query_rewriter=query_rewriter,
    frame_processor=frame_processor,
    embedding_ranker=embedding_ranker,
    data_store=data_store_factory.new(),
    thumbnail_generator=thumbnail_generator,
    temporary_storage = temporary_storage
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        user = auth_provider.get_current_user(credentials)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

@app.post("/index/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> None:
    user_id = current_user.id
    video_id = pipeline.generate_video_id()
    video_path = temporary_storage.store(user_id, video_id, file)
    pipeline.save_upload(user_id, video_id, video_path,
    {
        "status": "processing",
        "stage": "Transcribing...",
        "created_at" : str(datetime.datetime.now())
    })
    
    thumbnail = pipeline.generate_thumbnail(video_path)
    pipeline.save_thumbnail(user_id, video_id, thumbnail)
    
    background_tasks.add_task(
        pipeline.index_video_and_cleanup,
        user_id,
        video_id,
        video_path
    )

    return {"video_id": video_id}

@app.post("/search/{video_id}")
async def search(
    video_id: str,
    query: str,
    top_k: int = 10,
    current_user: User = Depends(get_current_user)
):
    video_data = pipeline.load_indexed_video(current_user.id, video_id)
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

@app.get("/videos")
async def get_all_videos(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    all_meta_data = pipeline.load_all_metadata(user_id)

    return [
        LightVideoResponse(
            video_id=metadata["id"],
            filename=metadata["filename"],
            thumbnail_url=pipeline.get_thumbnail_url(user_id, metadata["id"]),
            status=metadata["status"],
            stage=metadata["stage"],
            created_at=metadata["created_at"],
        )
        for metadata in all_meta_data
    ]

@app.get("/videos/{video_id}")
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user)
    ):
    return pipeline.get_video_url(current_user.id, video_id)

@app.post("/auth/login")
def sign_in(email: str, password: str):
    response = auth_provider.sign_in(
            email,
            password,
    )

    if not response.success:
        raise HTTPException(
            status_code=401,
            detail={
                "code": response.error_code,
                "message": response.error_message,
            },
        )

    return AuthResponse(
        email=response.email,
        access_token=response.access_token,
        refresh_token=response.refresh_token
    )

@app.post("/auth/signup")
def sign_up(email: str, password: str):
    response = auth_provider.sign_up(
            email,
            password,
    )

    if not response.success:
        raise HTTPException(
            status_code=401,
            detail={
                "code": response.error_code,
                "message": response.error_message,
            },
        )

    return AuthResponse(
        email=response.email,
        access_token=response.access_token,
        refresh_token=response.refresh_token
    )

@app.post("/auth/refresh")
def refresh(
    refresh_token: str
) -> AuthResponse:
    return auth_provider.refresh(
        refresh_token
    )