from io import BytesIO
from pathlib import Path
from fastapi import UploadFile
from backend.src.frame_finder.pipeline.classes.local_data_store import LocalDataStore
from backend.src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from backend.src.frame_finder.data_classes.video_frame import VideoFrame
import numpy as np
import pytest, torch

USERNAME = "alice"
VIDEO_ID = "video1"

def _segment(start: float, end: float, text: str) -> TranscriptSegment:
    return TranscriptSegment(
        start=start,
        end=end,
        text=text,
        embedding=torch.randn(512),
    )


def _frame(timestamp: float) -> VideoFrame:
    return VideoFrame(
        timestamp=timestamp,
        embedding=torch.randn(512),
    )


def _transcripts() -> list[TranscriptSegment]:
    return [
        _segment(0.0, 2.0, "Hello"),
        _segment(2.0, 4.0, "World"),
    ]


def _frames() -> list[VideoFrame]:
    return [
        _frame(0.0),
        _frame(1.5),
    ]


def _create_store(tmp_path: Path) -> LocalDataStore:
    return LocalDataStore(tmp_path)


def _create_upload(filename: str = "lecture.mp4") -> UploadFile:
    return UploadFile(
        file=BytesIO(b"fake video content"),
        filename=filename,
    )


def _save_video(
    store: LocalDataStore,
    username: str = USERNAME,
    video_id: str = VIDEO_ID,
    filename: str = "lecture.mp4",
    transcripts: list[TranscriptSegment] | None = None,
    frames: list[VideoFrame] | None = None,
):
    store.save_upload(
        username=username,
        video_id=video_id,
        file=_create_upload(filename),
        metadata={},
    )

    store.save_transcripts(
        username=username,
        video_id=video_id,
        transcript_segments=(
            _transcripts() if transcripts is None else transcripts
        ),
    )

    store.save_video_frames(
        username=username,
        video_id=video_id,
        video_frames=(
            _frames() if frames is None else frames
        ),
    )


def _assert_transcripts_equal(expected, actual):
    assert len(expected) == len(actual)

    for e, a in zip(expected, actual):
        assert e.start == a.start
        assert e.end == a.end
        assert e.text == a.text
        assert torch.equal(e.embedding, a.embedding)


def _assert_frames_equal(expected, actual):
    assert len(expected) == len(actual)

    for e, a in zip(expected, actual):
        assert e.timestamp == a.timestamp
        assert torch.equal(e.embedding, a.embedding)


def test_save_upload_creates_video_directory_and_metadata(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload("lecture.mp4"),
        metadata={},
    )

    directory = tmp_path / "alice" / "video1"

    assert directory.exists()
    assert (directory / "lecture.mp4").exists()
    assert (directory / "metadata.json").exists()


def test_save_transcripts_creates_expected_files(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload(),
        metadata={},
    )

    store.save_transcripts(
        username="alice",
        video_id="video1",
        transcript_segments=_transcripts(),
    )

    directory = tmp_path / "alice" / "video1"

    assert (directory / "transcript_metadata.json").exists()
    assert (directory / "transcript_embeddings.pt").exists()


def test_save_video_frames_creates_expected_files(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload(),
        metadata={},
    )

    store.save_video_frames(
        username="alice",
        video_id="video1",
        video_frames=_frames(),
    )

    directory = tmp_path / "alice" / "video1"

    assert (directory / "frame_metadata.json").exists()
    assert (directory / "frame_embeddings.pt").exists()


def test_load_returns_original_video_data(tmp_path):
    store = _create_store(tmp_path)

    original_transcripts = _transcripts()
    original_frames = _frames()

    _save_video(
        store,
        transcripts=original_transcripts,
        frames=original_frames,
    )

    loaded = store.load("alice", "video1")

    assert loaded.metadata == {
        "video_id": "video1",
        "username": "alice",
        "filename": "lecture.mp4",
    }

    assert loaded.video_path == (
        tmp_path / "alice" / "video1" / "lecture.mp4"
    )

    assert loaded.thumbnail_path == (
        tmp_path / "alice" / "video1" / "thumbnail.jpg"
    )

    _assert_transcripts_equal(
        original_transcripts,
        loaded.indexed_video.transcript_segments,
    )

    _assert_frames_equal(
        original_frames,
        loaded.indexed_video.video_frames,
    )


def test_save_upload_preserves_metadata(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload("lecture.mp4"),
        metadata={
            "title": "My Lecture",
            "duration": 120,
        },
    )

    loaded_metadata = store._load_meta_data(
        tmp_path / "alice" / "video1"
    )

    assert loaded_metadata == {
        "video_id": "video1",
        "username": "alice",
        "filename": "lecture.mp4",
        "title": "My Lecture",
        "duration": 120,
    }


def test_update_metadata(tmp_path):
    store = _create_store(tmp_path)

    _save_video(store)

    store.update_metadata(
        username="alice",
        video_id="video1",
        updates={
            "title": "Updated Lecture",
            "duration": 300,
        },
    )

    loaded = store.load("alice", "video1")

    assert loaded.metadata["title"] == "Updated Lecture"
    assert loaded.metadata["duration"] == 300
    assert loaded.metadata["filename"] == "lecture.mp4"


def test_load_missing_video_raises_file_not_found(tmp_path):
    store = _create_store(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.load("alice", "missing")


def test_load_missing_video_file_raises_file_not_found(tmp_path):
    store = _create_store(tmp_path)

    directory = tmp_path / "alice" / "video1"
    directory.mkdir(parents=True)

    store._save_meta_data(
        directory,
        {
            "video_id": "video1",
            "username": "alice",
            "filename": "lecture.mp4",
        },
    )

    with pytest.raises(FileNotFoundError):
        store.load("alice", "video1")


def test_save_and_load_empty_indexed_video(tmp_path):
    store = _create_store(tmp_path)

    _save_video(
        store,
        transcripts=[],
        frames=[],
    )

    loaded = store.load("alice", "video1")

    assert loaded.indexed_video.transcript_segments == []
    assert loaded.indexed_video.video_frames == []

    assert loaded.metadata["filename"] == "lecture.mp4"


def test_save_empty_transcripts_creates_empty_embeddings(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload(),
        metadata={},
    )

    store.save_transcripts(
        username="alice",
        video_id="video1",
        transcript_segments=[],
    )

    embeddings = torch.load(
        tmp_path
        / "alice"
        / "video1"
        / "transcript_embeddings.pt"
    )

    assert embeddings.shape == (0, 512)


def test_save_empty_video_frames_creates_empty_embeddings(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload(),
        metadata={},
    )

    store.save_video_frames(
        username="alice",
        video_id="video1",
        video_frames=[],
    )

    embeddings = torch.load(
        tmp_path
        / "alice"
        / "video1"
        / "frame_embeddings.pt"
    )

    assert embeddings.shape == (0, 512)


def test_load_all_returns_all_videos(tmp_path):
    store = _create_store(tmp_path)

    _save_video(
        store,
        video_id="video1",
        filename="lecture.mp4",
    )

    _save_video(
        store,
        video_id="video2",
        filename="cats.mp4",
    )

    videos = store.load_all("alice")

    assert len(videos) == 2

    filenames = {
        video.metadata["filename"]
        for video in videos
    }

    assert filenames == {
        "lecture.mp4",
        "cats.mp4",
    }


def test_load_all_returns_empty_list_when_user_has_no_videos(tmp_path):
    store = _create_store(tmp_path)

    (tmp_path / "alice").mkdir()

    videos = store.load_all("alice")

    assert videos == []


def test_load_all_missing_user_raises_file_not_found(tmp_path):
    store = _create_store(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.load_all("alice")

def test_save_thumbnail_creates_thumbnail(tmp_path):
    store = _create_store(tmp_path)

    store.save_upload(
        username="alice",
        video_id="video1",
        file=_create_upload(),
        metadata={},
    )

    thumbnail = np.zeros((100, 100, 3), dtype=np.uint8)

    store.save_thumbnail(
        username="alice",
        video_id="video1",
        thumbnail=thumbnail,
    )

    assert (
        tmp_path
        / "alice"
        / "video1"
        / "thumbnail.jpg"
    ).exists()