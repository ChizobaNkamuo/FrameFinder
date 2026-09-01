from typing import List
from pathlib import Path
from tempfile import TemporaryDirectory
from src.frame_finder.ml.interfaces.embedding_model import EmbeddingModel
from src.frame_finder.ml.interfaces.speech_transcriber import SpeechTranscriber
from src.frame_finder.pipeline.interfaces.frame_processor import FrameProcessor
from src.frame_finder.pipeline.interfaces.thumbnail_generator import ThumbnailGenerator
from src.frame_finder.pipeline.interfaces.file_downloader import FileDownloader
from src.frame_finder.data.interfaces.data_store import DataStore
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment

class WorkerPipeline:
    def __init__(self, 
                 speech_transcriber: SpeechTranscriber, embedding_model: EmbeddingModel,
                 frame_processor: FrameProcessor, data_store: DataStore,
                 thumbnail_generator: ThumbnailGenerator, file_downloader: FileDownloader
                 ):
        self._speech_transcriber = speech_transcriber
        self._embedding_model = embedding_model
        self._frame_processor = frame_processor
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

    def index_video(self, user_id: str, video_id: str, video_path: Path) -> None:
        transcripted_segments = self._speech_transcriber.transcribe(video_path)["segments"]
        processed_segments = self.process_segments(transcripted_segments)

        self._data_store.save_transcripts(
            user_id,
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
            user_id,
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
    
    def process_video(
        self,
        user_id: str,
        video_id: str,
    ):
        video_url = self._data_store.get_video_url(
            user_id,
            video_id,
        )

        with TemporaryDirectory() as temp_dir:
            video_path = Path(temp_dir) / video_id

            self._file_downloader.download(
                video_url,
                video_path,
            )

            self.index_video(
                user_id,
                video_id,
                video_path,
            )