from pydantic import BaseModel

class LightVideoResponse(BaseModel):
    video_id: str
    filename: str
    thumbnail_url: str
    status: str
    stage: str
    created_at: str