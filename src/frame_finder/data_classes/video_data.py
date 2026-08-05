from dataclasses import dataclass
from frame_finder.data_classes.indexed_video import IndexedVideo

@dataclass
class VideoData:
    indexed_video: IndexedVideo
    metadata: dict