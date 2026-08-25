from dataclasses import dataclass, field
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.video_frame import VideoFrame

@dataclass
class IndexedVideo:
    transcript_segments: list[TranscriptSegment] = field(default_factory=list)
    video_frames: list[VideoFrame] = field(default_factory=list)