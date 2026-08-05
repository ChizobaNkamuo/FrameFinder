from typing import List
from pathlib import Path
from frame_finder.pipeline.interfaces.data_store import DataStore
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.data_classes.transcript_segment import TranscriptSegment
from frame_finder.data_classes.video_frame import VideoFrame
from frame_finder.data_classes.video_data import VideoData
import torch, json

class LocalDataStore(DataStore):
    def __init__(self, root: Path):
        self._root = root

    def _save_transcripts(self, directory: Path, indexed_video: IndexedVideo) -> None:
        transcript_metadata = []
        transcript_embeddings = []

        for segment in indexed_video.transcript_segments:
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

    def _save_video_frames(self, directory: Path, indexed_video: IndexedVideo) -> None:
        frame_metadata = []
        frame_embeddings = []

        for frame in indexed_video.video_frames:
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

    def _load_transcripts(self, directory: Path) -> List[TranscriptSegment]:
        with open(directory / "transcript_metadata.json") as f:
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
        with open(directory / "frame_metadata.json") as f:
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

    def save(
        self,
        username: str,
        video_id: str,
        filename: str,
        indexed_video: IndexedVideo
    ) -> None:

        directory = self._root / username / video_id
        directory.mkdir(parents=True, exist_ok=True)

        metadata = {
            "video_id": video_id,
            "username": username,
            "filename": filename
        }

        with open(directory / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)

        self._save_transcripts(directory, indexed_video)
        self._save_video_frames(directory, indexed_video)

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

        with open(directory / "metadata.json") as f:
            metadata = json.load(f)

        transcript_segments = self._load_transcripts(directory)
        video_frames = self._load_embeddings(directory)

        indexed_video = IndexedVideo(
            transcript_segments,
            video_frames,
        )

        return VideoData(
            indexed_video,
            metadata
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