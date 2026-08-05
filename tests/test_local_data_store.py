from pathlib import Path
from frame_finder.pipeline.classes.local_data_store import LocalDataStore
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.data_classes.transcript_segment import TranscriptSegment
from frame_finder.data_classes.video_frame import VideoFrame
import torch, pytest

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


def _indexed_video() -> IndexedVideo:
    return IndexedVideo(
        transcript_segments=[
            _segment(0.0, 2.0, "Hello"),
            _segment(2.0, 4.0, "World"),
        ],
        video_frames=[
            _frame(0.0),
            _frame(1.5),
        ],
    )


def _create_store(tmp_path: Path) -> LocalDataStore:
    return LocalDataStore(tmp_path)


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


def test_save_creates_expected_files(tmp_path):
    store = _create_store(tmp_path)

    store.save(
        username="alice",
        video_id="video1",
        filename="lecture.mp4",
        indexed_video=_indexed_video(),
    )

    directory = tmp_path / "alice" / "video1"

    assert directory.exists()

    assert (directory / "metadata.json").exists()
    assert (directory / "transcript_metadata.json").exists()
    assert (directory / "transcript_embeddings.pt").exists()
    assert (directory / "frame_metadata.json").exists()
    assert (directory / "frame_embeddings.pt").exists()


def test_load_returns_original_video_data(tmp_path):
    store = _create_store(tmp_path)

    original = _indexed_video()

    store.save(
        username="alice",
        video_id="video1",
        filename="lecture.mp4",
        indexed_video=original,
    )

    loaded = store.load("alice", "video1")

    assert loaded.metadata == {
        "video_id": "video1",
        "username": "alice",
        "filename": "lecture.mp4",
    }

    _assert_transcripts_equal(
        original.transcript_segments,
        loaded.indexed_video.transcript_segments,
    )

    _assert_frames_equal(
        original.video_frames,
        loaded.indexed_video.video_frames,
    )


def test_load_missing_video_raises_file_not_found(tmp_path):
    store = _create_store(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.load("alice", "missing")


def test_save_and_load_empty_indexed_video(tmp_path):
    store = _create_store(tmp_path)

    empty = IndexedVideo(
        transcript_segments=[],
        video_frames=[],
    )

    store.save(
        username="alice",
        video_id="video1",
        filename="empty.mp4",
        indexed_video=empty,
    )

    loaded = store.load("alice", "video1")

    assert loaded.indexed_video.transcript_segments == []
    assert loaded.indexed_video.video_frames == []

    assert loaded.metadata["filename"] == "empty.mp4"


def test_load_all_returns_all_videos(tmp_path):
    store = _create_store(tmp_path)

    store.save(
        "alice",
        "video1",
        "lecture.mp4",
        _indexed_video(),
    )

    store.save(
        "alice",
        "video2",
        "cats.mp4",
        _indexed_video(),
    )

    videos = store.load_all("alice")

    assert len(videos) == 2

    filenames = {video.metadata["filename"] for video in videos}

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