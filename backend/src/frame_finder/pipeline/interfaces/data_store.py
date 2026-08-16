from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from fastapi import UploadFile
from backend.src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from backend.src.frame_finder.data_classes.video_frame import VideoFrame
from backend.src.frame_finder.data_classes.video_data import VideoData
import numpy as np

class DataStore(ABC):
    """
        @abstractmethod
        def save(
            self,
            username: str,
            video_id: str,
            filename: str,
            indexed_video: IndexedVideo
        ) -> None:
            pass
    """
    @abstractmethod
    def save_transcripts(
        self,
        username: str,
        video_id: str,
        transcript_segments: List[TranscriptSegment],
    ) -> None:
        pass

    @abstractmethod
    def save_video_frames(
        self,
        username: str,
        video_id: str,
        video_frames: List[VideoFrame],
    ) -> None:
        pass

    @abstractmethod
    def save_upload(
        self,
        username: str,
        video_id: str,
        file: UploadFile,
        metadata: dict
    ) -> Path:
        pass

    @abstractmethod
    def save_thumbnail(
        self,
        username: str,
        video_id: str,
        thumbnail: np.ndarray,
    ) -> None:
        pass

    @abstractmethod
    def update_metadata(
        self,
        username: str,
        video_id: str,
        updates: dict,
    ) -> None:
        pass

    @abstractmethod
    def load(
        self,
        username: str,
        video_id: str,
    ) -> VideoData:
        pass

    @abstractmethod
    def load_all(
        self,
        username: str,
    ) -> List[VideoData]:
        pass

