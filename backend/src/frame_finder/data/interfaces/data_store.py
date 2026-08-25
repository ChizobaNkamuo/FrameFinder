from abc import ABC, abstractmethod
from typing import List
from fastapi import UploadFile
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.video_frame import VideoFrame
from src.frame_finder.data_classes.video_data import VideoData
from pathlib import Path
import numpy as np

class DataStore(ABC):
    @abstractmethod
    def save_transcripts(
        self,
        user_id: str,
        video_id: str,
        transcript_segments: List[TranscriptSegment],
    ) -> None:
        pass

    @abstractmethod
    def save_video_frames(
        self,
        user_id: str,
        video_id: str,
        video_frames: List[VideoFrame],
    ) -> None:
        pass

    @abstractmethod
    def save_upload(
        self,
        user_id: str,
        video_id: str,
        video_path: Path,
        metadata: dict
    ) -> None:
        pass

    @abstractmethod
    def save_thumbnail(
        self,
        user_id: str,
        video_id: str,
        thumbnail: np.ndarray,
    ) -> None:
        pass

    @abstractmethod
    def update_metadata(
        self,
        user_id: str,
        video_id: str,
        updates: dict,
    ) -> None:
        pass

    @abstractmethod
    def load_all_metadata(
        self,
        user_id: str,
    ) -> List[dict]:
        pass

    @abstractmethod
    def get_thumbnail_url(
        self,
        user_id: str,
        video_id: str,
    ) -> str:
        pass

    @abstractmethod
    def get_video_url(
        self,
        user_id: str,
        video_id: str,
    ) -> str:
        pass

    @abstractmethod
    def load_indexed_video(
        self,
        user_id: str,
        video_id: str,
    ) -> VideoData:
        pass
