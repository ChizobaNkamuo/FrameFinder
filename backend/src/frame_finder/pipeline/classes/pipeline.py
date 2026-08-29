from typing import List
from pathlib import Path
from tempfile import TemporaryDirectory
from fastapi import UploadFile
from src.frame_finder.ml.interfaces.embedding_model import EmbeddingModel
from src.frame_finder.ml.interfaces.speech_transcriber import SpeechTranscriber
from src.frame_finder.pipeline.interfaces.query_classifier import QueryClassifier
from src.frame_finder.ml.interfaces.query_rewriter import QueryRewriter
from src.frame_finder.pipeline.interfaces.frame_processor import FrameProcessor
from src.frame_finder.pipeline.interfaces.embedding_ranker import EmbeddingRanker
from src.frame_finder.pipeline.interfaces.thumbnail_generator import ThumbnailGenerator
from src.frame_finder.pipeline.interfaces.file_downloader import FileDownloader
from src.frame_finder.data.interfaces.data_store import DataStore
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.indexed_video import IndexedVideo
from src.frame_finder.data_classes.query import Query
from src.frame_finder.data_classes.embeddable import Embeddable
from src.frame_finder.data_classes.video_data import VideoData
import numpy as np
import uuid, datetime, shutil

class Pipeline:
    def __init__(self, 
                 speech_transcriber: SpeechTranscriber, embedding_model: EmbeddingModel,
                 query_classifier: QueryClassifier, query_rewriter: QueryRewriter,
                 frame_processor: FrameProcessor, embedding_ranker: EmbeddingRanker,
                 data_store: DataStore, thumbnail_generator: ThumbnailGenerator,
                 file_downloader: FileDownloader
                 ):
        self._speech_transcriber = speech_transcriber
        self._embedding_model = embedding_model
        self._query_classifier = query_classifier
        self._query_rewriter = query_rewriter
        self._frame_processor = frame_processor
        self._embedding_ranker = embedding_ranker
        self._data_store = data_store
        self._thumbnail_generator = thumbnail_generator
        self._file_downloader = file_downloader

    def process_segments(
        self,
        segments: List[dict]
    ) -> List[TranscriptSegment]:

        transcript_segments = []

        for segment in segments:
            embedding = self._embedding_model.embed_text(segment["text"])
        
            transcript_segments.append(
                TranscriptSegment(
                    text=segment["text"],
                    start=segment["start"],
                    end=segment["end"],
                    embedding=embedding,
                )
            )

        return transcript_segments

    def rank_embeddings(
        self,
        query_embedding: np.ndarray,
        items: List[Embeddable],
    ) -> List[Embeddable]:
        return self._embedding_ranker.rank_embeddings(query_embedding, items)

    def extract_query_info(self, query: str) -> Query:
        rewritten_query = self._query_rewriter.rewrite(query)
        classification = self._query_classifier.classify(query)
        query_embedding = self._embedding_model.embed_text(rewritten_query)

        return Query(
            intent=rewritten_query,
            classification=classification,
            embedding=query_embedding
            )

    def get_ranked_video(self, formatted_query: Query, indexed_video: IndexedVideo, top_k: int) -> IndexedVideo:
        query_classification = formatted_query.classification
        ranked_transcript_segments, ranked_video_frames = [], []

        if query_classification == "speech" or query_classification == "both":
            ranked_transcript_segments = self.rank_embeddings(formatted_query.embedding, indexed_video.transcript_segments)
            max_speech_index = min(top_k, len(ranked_transcript_segments))
            ranked_transcript_segments = ranked_transcript_segments[:max_speech_index]
                
        if query_classification == "vision" or query_classification == "both":
            ranked_video_frames = self.rank_embeddings(formatted_query.embedding, indexed_video.video_frames)
            max_vision_index = min(top_k, len(ranked_video_frames))
            ranked_video_frames = ranked_video_frames[:max_vision_index]

        return IndexedVideo(transcript_segments=ranked_transcript_segments, video_frames=ranked_video_frames)

    def generate_thumbnail(self, video_path: Path) -> np.ndarray:
        return self._thumbnail_generator.generate_thumbnail(video_path)

    def save_thumbnail(
        self,
        user_id: str,
        video_id: str,
        thumbnail: np.ndarray,
    ):
        self._data_store.save_thumbnail(user_id, video_id, thumbnail)

    def save_upload(
        self,
        user_id: str,
        video_id: str,
        video_path: Path,
        metadata: dict
    ) -> None:
        return self._data_store.save_upload(user_id, video_id, video_path, metadata)

    def generate_video_id(self):
        return str(uuid.uuid4())

    def index_video(self, user_id: str, video_id: str, video_path: Path) -> None:
        transcripted_segments = self._speech_transcriber.transcribe(video_path)["segments"]
        processed_segments = self.process_segments(transcripted_segments)

        self._data_store.save_transcripts(
            video_id,
            processed_segments,
        )     

        self._data_store.update_metadata(
            user_id,
            video_id,
            {"stage": "Processing frames..."},
        )

        processed_frames = self._frame_processor.process_frames(video_path, 10)   
        self._data_store.save_video_frames(
            video_id,
            processed_frames,
        )     
        
        self._data_store.update_metadata(
            user_id,
            video_id,
            {
                "status": "complete",
                "stage": "",
            },
        )

    def load_indexed_video(self, user_id: str, video_id: str) -> VideoData:
        return self._data_store.load_indexed_video(user_id, video_id)

    def get_thumbnail_url(self, user_id: str, video_id: str) -> str:
        return self._data_store.get_thumbnail_url(user_id, video_id)

    def get_video_url(self, user_id: str, video_id: str) -> str:
        return self._data_store.get_video_url(user_id, video_id)

    def load_all_metadata(self, user_id: str) -> List[dict]:
        return self._data_store.load_all_metadata(user_id)
    
    def process_video(
        self,
        user_id: str,
        video_id: str,
    ):
        video_url = self.get_video_url(
            user_id,
            video_id,
        )

        with TemporaryDirectory() as temp_dir:
            video_path = temp_dir / video_id

            self._file_downloader.download(
                video_url,
                video_path,
            )

            self.index_video(
                user_id,
                video_id,
                video_path,
            )

    def upload_video(self, user_id: str, file: UploadFile) -> str:
        video_id = self.generate_video_id()

        with TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / file.filename

            with video_path.open("wb") as buffer:
                shutil.copyfileobj(
                    file.file,
                    buffer,
                )

            self.save_upload(user_id, video_id, video_path,
            {
                "status": "processing",
                "stage": "Transcribing...",
                "created_at" : str(datetime.datetime.now())
            })
            
            thumbnail = self.generate_thumbnail(video_path)
            self.save_thumbnail(user_id, video_id, thumbnail)

        return video_id