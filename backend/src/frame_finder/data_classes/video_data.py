from dataclasses import dataclass
from src.frame_finder.data_classes.indexed_video import IndexedVideo
from pathlib import Path

@dataclass
class VideoData:
    indexed_video: IndexedVideo
    metadata: dict