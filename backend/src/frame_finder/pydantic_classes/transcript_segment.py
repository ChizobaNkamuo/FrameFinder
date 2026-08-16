from pydantic import BaseModel

class TranscriptSegment(BaseModel):
    timestamp: int
    text: str
