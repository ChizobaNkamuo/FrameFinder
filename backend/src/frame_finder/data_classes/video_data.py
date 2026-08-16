from dataclasses import dataclass
from backend.src.frame_finder.data_classes.indexed_video import IndexedVideo
from pathlib import Path

@dataclass
class VideoData:
    indexed_video: IndexedVideo
    metadata: dict
    video_path: Path
    thumbnail_path: Path