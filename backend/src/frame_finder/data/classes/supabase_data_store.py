from typing import List

from supabase import Client

from src.frame_finder.data.interfaces.data_store import DataStore
from src.frame_finder.data_classes.indexed_video import IndexedVideo
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.video_frame import VideoFrame
from src.frame_finder.data_classes.video_data import VideoData
from pathlib import Path
import torch, cv2, json
import numpy as np

class SupabaseDataStore(DataStore):

    _VIDEO_BUCKET = "videos"

    def __init__(
        self,
        client: Client
    ):
        self._client = client

    def _to_tensor(
        self,
        embedding: list[float] | str,
    ) -> torch.Tensor:
        
        embedding = json.loads(embedding)

        return torch.tensor(
            embedding,
            dtype=torch.float32,
        )

    def _load_transcripts(
        self,
        video_id: str,
    ) -> List[TranscriptSegment]:

        response = (
            self._client
            .table("transcript_segments")
            .select("*")
            .eq("video_id", video_id)
            .order("start")
            .execute()
        )

        return [
            TranscriptSegment(
                start=row["start"],
                end=row["end"],
                text=row["text"],
                embedding=self._to_tensor(row["embedding"]),
            )
            for row in response.data
        ]

    def _load_video_frames(
        self,
        video_id: str,
    ) -> List[VideoFrame]:

        response = (
            self._client
            .table("video_frames")
            .select("*")
            .eq("video_id", video_id)
            .order("timestamp")
            .execute()
        )

        return [
            VideoFrame(
                timestamp=row["timestamp"],
                embedding=self._to_tensor(row["embedding"]),
            )
            for row in response.data
        ]

    def save_upload(
        self,
        user_id: str,
        video_id: str,
        video_path: Path,
        metadata: dict,
    ) -> None:
        filename = video_path.name

        storage_path = (
            f"{user_id}/{video_id}/{filename}"
        )

        self._client.storage.from_(
            self._VIDEO_BUCKET
        ).upload(
            path=storage_path,
            file=video_path,
            file_options={
                "content-type": "video/mp4",
            },
        )

        self._client.table(
            "videos"
        ).insert(
            {
                "id": video_id,
                "user_id": user_id,
                "filename": filename,
                **metadata,
            }
        ).execute()

    def save_transcripts(
        self,
        user_id: str,
        video_id: str,
        transcript_segments: List[TranscriptSegment],
    ) -> None:

        if not transcript_segments:
            return

        rows = []

        for segment in transcript_segments:

            embedding = (
                segment.embedding
                .detach()
                .cpu()
                .tolist()
            )

            rows.append(
                {
                    "video_id": video_id,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "embedding": embedding,
                }
            )

        self._client.table(
            "transcript_segments"
        ).insert(rows).execute()

    def save_video_frames(
        self,
        user_id: str,
        video_id: str,
        video_frames: List[VideoFrame],
    ) -> None:

        if not video_frames:
            return

        rows = []

        for frame in video_frames:

            embedding = (
                frame.embedding
                .detach()
                .cpu()
                .tolist()
            )

            rows.append(
                {
                    "video_id": video_id,
                    "timestamp": frame.timestamp,
                    "embedding": embedding,
                }
            )

        self._client.table(
            "video_frames"
        ).insert(rows).execute()

    def save_thumbnail(
        self,
        user_id: str,
        video_id: str,
        thumbnail: np.ndarray,
    ) -> None:

        success, encoded_thumbnail = cv2.imencode(
            ".jpg",
            thumbnail,
        )

        if not success:
            raise ValueError(
                "Failed to encode thumbnail."
            )

        storage_path = (
            f"{user_id}/{video_id}/thumbnail.jpg"
        )

        self._client.storage.from_(
            self._VIDEO_BUCKET
        ).upload(
            path=storage_path,
            file=encoded_thumbnail.tobytes(),
            file_options={
                "content-type": "image/jpeg",
                "upsert": "true",
            },
        )

    def update_metadata(
        self,
        user_id: str,
        video_id: str,
        updates: dict,
    ) -> None:

        self._client.table(
            "videos"
        ).update(
            updates
        ).eq(
            "id",
            video_id,
        ).eq(
            "user_id",
            user_id,
        ).execute()

    def load_indexed_video(
        self,
        user_id: str,
        video_id: str,
    ) -> VideoData:

        video_response = (
            self._client
            .table("videos")
            .select("*")
            .eq("id", video_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        metadata = video_response.data

        transcript_segments = self._load_transcripts(
            video_id
        )

        video_frames = self._load_video_frames(
            video_id
        )

        indexed_video = IndexedVideo(
            transcript_segments=transcript_segments,
            video_frames=video_frames,
        )

        return VideoData(
            indexed_video=indexed_video,
            metadata=metadata,
        )

    def get_video_url(
        self,
        user_id: str,
        video_id: str,
    ) -> str:

        response = (
            self._client
            .table("videos")
            .select("filename")
            .eq("id", video_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        filename = response.data["filename"]

        storage_path = (
            f"{user_id}/{video_id}/{filename}"
        )

        signed_url_response = (
            self._client
            .storage
            .from_(self._VIDEO_BUCKET)
            .create_signed_url(
                path=storage_path,
                expires_in=3600,
            )
        )

        return signed_url_response["signedURL"]

    def get_thumbnail_url(
        self,
        user_id: str,
        video_id: str,
    ) -> str:

        storage_path = (
            f"{user_id}/{video_id}/thumbnail.jpg"
        )

        signed_url_response = (
            self._client
            .storage
            .from_(self._VIDEO_BUCKET)
            .create_signed_url(
                path=storage_path,
                expires_in=3600,
            )
        )

        return signed_url_response["signedURL"]

    def load_all_metadata(
        self,
        user_id: str,
    ) -> List[dict]:

        response = (
            self._client
            .table("videos")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        videos = []

        for metadata in response.data:
            videos.append(
                metadata
            )

        return videos