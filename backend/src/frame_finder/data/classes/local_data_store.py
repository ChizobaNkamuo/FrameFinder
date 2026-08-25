from typing import List
from pathlib import Path

from src.frame_finder.data.interfaces.data_store import DataStore
from src.frame_finder.data_classes.indexed_video import IndexedVideo
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.video_frame import VideoFrame
from src.frame_finder.data_classes.video_data import VideoData

import json
import shutil
import cv2
import torch
import numpy as np


class LocalDataStore(DataStore):

    def __init__(
        self,
        root: Path,
    ):
        self._root = root


    def _get_directory(
        self,
        user_id: str,
        video_id: str,
    ) -> Path:

        return (
            self._root
            / user_id
            / video_id
        )


    def _save_metadata(
        self,
        directory: Path,
        metadata: dict,
    ) -> None:

        with open(
            directory / "metadata.json",
            "w",
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4,
            )


    def _load_metadata(
        self,
        user_id: str,
        video_id: str,
    ) -> dict:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        metadata_path = (
            directory
            / "metadata.json"
        )

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"No metadata found for video "
                f"'{video_id}'."
            )

        with open(metadata_path) as file:
            return json.load(file)


    def _load_transcripts(
        self,
        user_id: str,
        video_id: str,
    ) -> List[TranscriptSegment]:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        metadata_path = (
            directory
            / "transcript_metadata.json"
        )

        embeddings_path = (
            directory
            / "transcript_embeddings.pt"
        )

        if (
            not metadata_path.exists()
            or not embeddings_path.exists()
        ):
            return []

        with open(metadata_path) as file:
            transcript_metadata = json.load(file)

        transcript_embeddings = torch.load(
            embeddings_path,
        )

        return [
            TranscriptSegment(
                start=metadata["start"],
                end=metadata["end"],
                text=metadata["text"],
                embedding=embedding,
            )
            for metadata, embedding in zip(
                transcript_metadata,
                transcript_embeddings,
            )
        ]


    def _load_video_frames(
        self,
        user_id: str,
        video_id: str,
    ) -> List[VideoFrame]:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        metadata_path = (
            directory
            / "frame_metadata.json"
        )

        embeddings_path = (
            directory
            / "frame_embeddings.pt"
        )

        if (
            not metadata_path.exists()
            or not embeddings_path.exists()
        ):
            return []

        with open(metadata_path) as file:
            frame_metadata = json.load(file)

        frame_embeddings = torch.load(
            embeddings_path,
        )

        return [
            VideoFrame(
                timestamp=metadata["timestamp"],
                embedding=embedding,
            )
            for metadata, embedding in zip(
                frame_metadata,
                frame_embeddings,
            )
        ]


    def save_upload(
        self,
        user_id: str,
        video_id: str,
        video_path: Path,
        metadata: dict,
    ) -> None:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = (
            directory
            / video_path.name
        )

        shutil.copy2(
            video_path,
            destination,
        )

        self._save_metadata(
            directory,
            {
                "id": video_id,
                "user_id": user_id,
                "filename": video_path.name,
                **metadata,
            },
        )


    def save_transcripts(
        self,
        user_id: str,
        video_id: str,
        transcript_segments: List[TranscriptSegment],
    ) -> None:

        directory = self._get_directory(
            user_id,
            video_id,
        )

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

            transcript_embeddings.append(
                segment.embedding
                .detach()
                .cpu()
            )

        if transcript_embeddings:

            embeddings = torch.stack(
                transcript_embeddings,
            )

        else:

            embeddings = torch.empty(
                (0, 512),
                dtype=torch.float32,
            )

        torch.save(
            embeddings,
            directory
            / "transcript_embeddings.pt",
        )

        with open(
            directory
            / "transcript_metadata.json",
            "w",
        ) as file:

            json.dump(
                transcript_metadata,
                file,
                indent=4,
            )


    def save_video_frames(
        self,
        user_id: str,
        video_id: str,
        video_frames: List[VideoFrame],
    ) -> None:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        frame_metadata = []
        frame_embeddings = []

        for frame in video_frames:

            frame_metadata.append(
                {
                    "timestamp": frame.timestamp,
                }
            )

            frame_embeddings.append(
                frame.embedding
                .detach()
                .cpu()
            )

        if frame_embeddings:

            embeddings = torch.stack(
                frame_embeddings,
            )

        else:

            embeddings = torch.empty(
                (0, 512),
                dtype=torch.float32,
            )

        torch.save(
            embeddings,
            directory
            / "frame_embeddings.pt",
        )

        with open(
            directory
            / "frame_metadata.json",
            "w",
        ) as file:

            json.dump(
                frame_metadata,
                file,
                indent=4,
            )


    def save_thumbnail(
        self,
        user_id: str,
        video_id: str,
        thumbnail: np.ndarray,
    ) -> None:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        success = cv2.imwrite(
            str(
                directory
                / "thumbnail.jpg"
            ),
            thumbnail,
        )

        if not success:
            raise ValueError(
                "Failed to save thumbnail."
            )


    def update_metadata(
        self,
        user_id: str,
        video_id: str,
        updates: dict,
    ) -> None:

        directory = self._get_directory(
            user_id,
            video_id,
        )

        metadata = self._load_metadata(
            user_id,
            video_id,
        )

        metadata.update(
            updates,
        )

        self._save_metadata(
            directory,
            metadata,
        )


    def load_indexed_video(
        self,
        user_id: str,
        video_id: str,
    ) -> VideoData:

        metadata = self._load_metadata(
            user_id,
            video_id,
        )

        transcript_segments = (
            self._load_transcripts(
                user_id,
                video_id,
            )
        )

        video_frames = (
            self._load_video_frames(
                user_id,
                video_id,
            )
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

        metadata = self._load_metadata(
            user_id,
            video_id,
        )

        video_path = (
            self._get_directory(
                user_id,
                video_id,
            )
            / metadata["filename"]
        )

        if not video_path.exists():
            raise FileNotFoundError(
                f"Video file not found at "
                f"'{video_path}'."
            )

        return str(
            video_path.absolute(),
        )


    def get_thumbnail_url(
        self,
        user_id: str,
        video_id: str,
    ) -> str:

        thumbnail_path = (
            self._get_directory(
                user_id,
                video_id,
            )
            / "thumbnail.jpg"
        )

        if not thumbnail_path.exists():
            raise FileNotFoundError(
                f"Thumbnail not found at "
                f"'{thumbnail_path}'."
            )

        return str(
            thumbnail_path.absolute(),
        )


    def load_all_metadata(
        self,
        user_id: str,
    ) -> List[dict]:

        user_directory = (
            self._root
            / user_id
        )

        if not user_directory.exists():
            return []

        metadata_list = []

        for directory in user_directory.iterdir():

            if not directory.is_dir():
                continue

            metadata_path = (
                directory
                / "metadata.json"
            )

            if not metadata_path.exists():
                continue

            with open(metadata_path) as file:

                metadata_list.append(
                    json.load(file),
                )

        return metadata_list