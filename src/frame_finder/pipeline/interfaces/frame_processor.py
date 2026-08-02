from abc import ABC, abstractmethod
from frame_finder.data_classes.video_frame import VideoFrame
from typing import List

class FrameProcessor(ABC):
    @abstractmethod
    def process_frames(
        self,
        video_path: str,
        sample_rate: float,
    ) -> List[VideoFrame]:
        pass