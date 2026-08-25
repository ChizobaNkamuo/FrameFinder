from pydantic import BaseModel, Field
from src.frame_finder.pydantic_classes.transcript_segment import TranscriptSegment
from src.frame_finder.pydantic_classes.video_frame import VideoFrame

class SearchResponse(BaseModel):
    video_frames: list[VideoFrame] = Field(default_factory=list)
    transcript_segments: list[TranscriptSegment] = Field(default_factory=list)