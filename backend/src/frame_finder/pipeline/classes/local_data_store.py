from typing import List
from pathlib import Path
from backend.src.frame_finder.pipeline.interfaces.data_store import DataStore
from backend.src.frame_finder.data_classes.indexed_video import IndexedVideo
from backend.src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from backend.src.frame_finder.data_classes.video_frame import VideoFrame
from backend.src.frame_finder.data_classes.video_data import VideoData
from fastapi import UploadFile
import numpy as np
import torch, json, cv2, shutil

class LocalDataStore(DataStore):
    def __init__(self, root: Path):
        self._root = root

    def save_transcripts(
        self,
        username: str,
        video_id: str,
        transcript_segments: List[TranscriptSegment],
    ) -> None:

        directory = self._root / username / video_id
        transcript_metadata = []
        transcript_embeddings = []

        for segment in transcript_segments:
            transcript_metadata.append(
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                }
            )

            transcript_embeddings.append(segment.embedding)

        if transcript_embeddings:
            embeddings = torch.stack(transcript_embeddings)
        else:
            embeddings = torch.empty((0, 512))

        torch.save(
            embeddings,
            directory / "transcript_embeddings.pt",
        )

        with open(directory / "transcript_metadata.json", "w") as f:
            json.dump(transcript_metadata, f, indent=4)

    def save_video_frames(
        self,
        username: str,
        video_id: str,
        video_frames: List[VideoFrame],
    ) -> None:

        directory = self._root / username / video_id
        frame_metadata = []
        frame_embeddings = []

        for frame in video_frames:
            frame_metadata.append(
                {
                    "timestamp": frame.timestamp,
                }
            )

            frame_embeddings.append(frame.embedding)

        if frame_embeddings:
            embeddings = torch.stack(frame_embeddings)
        else:
            embeddings = torch.empty((0, 512))

        torch.save(
            embeddings,
            directory / "frame_embeddings.pt",
        )

        with open(directory / "frame_metadata.json", "w") as f:
            json.dump(frame_metadata, f, indent=4)

    def _save_meta_data(self, directory: Path, metadata: dict) -> None:
        with open(directory / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)    

    def _load_transcripts(self, directory: Path) -> List[TranscriptSegment]:
        file_path = directory / "transcript_metadata.json"

        if not file_path.exists():
            return []

        with open(file_path) as f:
            transcript_metadata = json.load(f)

        transcript_embeddings = torch.load(
            directory / "transcript_embeddings.pt"
        )

        transcript_segments = []

        for metadata, embedding in zip(transcript_metadata, transcript_embeddings):
            transcript_segments.append(
                TranscriptSegment(
                    start=metadata["start"],
                    end=metadata["end"],
                    text=metadata["text"],
                    embedding=embedding,
                )
            )
        return transcript_segments

    def _load_embeddings(self, directory: Path) -> List[VideoFrame]:
        file_path = directory / "frame_metadata.json"

        if not file_path.exists():
            return []
        
        with open(file_path) as f:
            frame_metadata = json.load(f)

        frame_embeddings = torch.load(
            directory / "frame_embeddings.pt"
        )

        video_frames = []

        for metadata, embedding in zip(frame_metadata, frame_embeddings):
            video_frames.append(
                VideoFrame(
                    timestamp=metadata["timestamp"],
                    embedding=embedding,
                )
            )
        return video_frames

    def _load_meta_data(self, directory: Path) -> dict:
        with open(directory / "metadata.json") as f:
            metadata = json.load(f)
        return metadata

    def save_upload(
        self,
        username: str,
        video_id: str,
        file: UploadFile,
        metadata: dict
    ) -> Path:
        filename = file.filename
        directory = self._root / username / video_id
        directory.mkdir(parents=True, exist_ok=True)

        file_path = directory / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        self._save_meta_data(
            directory,
            {
                "video_id": video_id,
                "username": username,
                "filename": filename,
                **metadata,
            },
        )        
        return file_path

    def save_thumbnail(
        self,
        username: str,
        video_id: str,
        thumbnail: np.ndarray,
    ) -> None:
        directory = self._root / username / video_id

        cv2.imwrite(
            str(directory / "thumbnail.jpg"),
            thumbnail,
        )

    def update_metadata(
        self,
        username: str,
        video_id: str,
        updates: dict,
    ) -> None:

        directory = self._root / username / video_id

        with open(directory / "metadata.json") as f:
            metadata = json.load(f)

        metadata.update(updates)

        self._save_meta_data(directory, metadata)

    def load(
        self,
        username: str,
        video_id: str,
    ) -> VideoData:

        directory = self._root / username / video_id

        if not directory.exists():
            raise FileNotFoundError(
                f"No indexed video found at '{directory}'."
            )

        metadata = self._load_meta_data(directory)
        video_path = directory / metadata["filename"]

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video file not found at '{video_path}'."
            )

        transcript_segments = self._load_transcripts(directory)
        video_frames = self._load_embeddings(directory)

        indexed_video = IndexedVideo(
            transcript_segments=transcript_segments,
            video_frames=video_frames,
        )

        return VideoData(
            indexed_video=indexed_video,
            metadata=metadata,
            video_path=video_path,
            thumbnail_path=video_path.parent / ("thumbnail.jpg")
            )

    def load_all(
        self,
        username: str,
    ) -> List[VideoData]:
            user_directory = self._root / username

            if not user_directory.exists():
                raise FileNotFoundError(
                    f"No videos found for user '{username}'."
                )

            videos = []

            for directory in user_directory.iterdir():

                if not directory.is_dir():
                    continue

                videos.append(
                    self.load(
                        username=username,
                        video_id=directory.name,
                    )
                )
            return videos