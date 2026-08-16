from abc import ABC, abstractmethod
from backend.src.frame_finder.data_classes.video_frame import VideoFrame
from typing import List
from pathlib import Path

class FrameProcessor(ABC):
    @abstractmethod
    def process_frames(
        self,
        video_path: Path,
        sample_rate: float,
    ) -> List[VideoFrame]:
        pass