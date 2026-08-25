
from src.frame_finder.data.classes.local_data_store import LocalDataStore
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.video_frame import VideoFrame
from pathlib import Path
import pytest, torch
import numpy as np



USER_ID = "alice"
VIDEO_ID = "video1"


def _segment(
    start: float,
    end: float,
    text: str,
) -> TranscriptSegment:

    return TranscriptSegment(
        start=start,
        end=end,
        text=text,
        embedding=torch.randn(512),
    )


def _frame(
    timestamp: float,
) -> VideoFrame:

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


def _create_store(
    tmp_path: Path,
) -> LocalDataStore:

    return LocalDataStore(
        tmp_path / "data",
    )


def _create_video(
    tmp_path: Path,
    filename: str = "lecture.mp4",
) -> Path:

    video_path = (
        tmp_path
        / filename
    )

    video_path.write_bytes(
        b"fake video content",
    )

    return video_path


def _save_video(
    store: LocalDataStore,
    tmp_path: Path,
    user_id: str = USER_ID,
    video_id: str = VIDEO_ID,
    filename: str = "lecture.mp4",
    metadata: dict | None = None,
    transcripts: list[TranscriptSegment] | None = None,
    frames: list[VideoFrame] | None = None,
) -> Path:

    video_path = _create_video(
        tmp_path,
        filename,
    )

    store.save_upload(
        user_id=user_id,
        video_id=video_id,
        video_path=video_path,
        metadata=metadata or {},
    )

    store.save_transcripts(
        user_id=user_id,
        video_id=video_id,
        transcript_segments=(
            _transcripts()
            if transcripts is None
            else transcripts
        ),
    )

    store.save_video_frames(
        user_id=user_id,
        video_id=video_id,
        video_frames=(
            _frames()
            if frames is None
            else frames
        ),
    )

    return video_path


def _assert_transcripts_equal(
    expected: list[TranscriptSegment],
    actual: list[TranscriptSegment],
) -> None:

    assert len(expected) == len(actual)

    for expected_segment, actual_segment in zip(
        expected,
        actual,
    ):
        assert (
            expected_segment.start
            == actual_segment.start
        )

        assert (
            expected_segment.end
            == actual_segment.end
        )

        assert (
            expected_segment.text
            == actual_segment.text
        )

        assert torch.equal(
            expected_segment.embedding,
            actual_segment.embedding,
        )


def _assert_frames_equal(
    expected: list[VideoFrame],
    actual: list[VideoFrame],
) -> None:

    assert len(expected) == len(actual)

    for expected_frame, actual_frame in zip(
        expected,
        actual,
    ):
        assert (
            expected_frame.timestamp
            == actual_frame.timestamp
        )

        assert torch.equal(
            expected_frame.embedding,
            actual_frame.embedding,
        )

def test_save_upload_creates_video_directory_and_metadata(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    video_path = _create_video(
        tmp_path,
    )

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={},
    )

    directory = (
        tmp_path
        / "data"
        / USER_ID
        / VIDEO_ID
    )

    assert directory.exists()

    assert (
        directory
        / "lecture.mp4"
    ).exists()

    assert (
        directory
        / "metadata.json"
    ).exists()

def test_save_upload_preserves_metadata(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    video_path = _create_video(
        tmp_path,
    )

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={
            "title": "My Lecture",
            "duration": 120,
        },
    )

    metadata = (
        store.load_all_metadata(
            USER_ID,
        )[0]
    )

    assert metadata == {
        "id": VIDEO_ID,
        "user_id": USER_ID,
        "filename": "lecture.mp4",
        "title": "My Lecture",
        "duration": 120,
    }

def test_save_transcripts_creates_expected_files(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    video_path = _create_video(
        tmp_path,
    )

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={},
    )

    store.save_transcripts(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        transcript_segments=_transcripts(),
    )

    directory = (
        tmp_path
        / "data"
        / USER_ID
        / VIDEO_ID
    )

    assert (
        directory
        / "transcript_metadata.json"
    ).exists()

    assert (
        directory
        / "transcript_embeddings.pt"
    ).exists()

def test_save_video_frames_creates_expected_files(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    video_path = _create_video(
        tmp_path,
    )

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={},
    )

    store.save_video_frames(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_frames=_frames(),
    )

    directory = (
        tmp_path
        / "data"
        / USER_ID
        / VIDEO_ID
    )

    assert (
        directory
        / "frame_metadata.json"
    ).exists()

    assert (
        directory
        / "frame_embeddings.pt"
    ).exists()

def test_load_indexed_video_returns_original_video_data(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    original_transcripts = (
        _transcripts()
    )

    original_frames = (
        _frames()
    )

    _save_video(
        store,
        tmp_path,
        transcripts=original_transcripts,
        frames=original_frames,
    )

    loaded = store.load_indexed_video(
        USER_ID,
        VIDEO_ID,
    )

    assert loaded.metadata == {
        "id": VIDEO_ID,
        "user_id": USER_ID,
        "filename": "lecture.mp4",
    }

    _assert_transcripts_equal(
        original_transcripts,
        loaded.indexed_video.transcript_segments,
    )

    _assert_frames_equal(
        original_frames,
        loaded.indexed_video.video_frames,
    )

def test_load_indexed_video_missing_video_raises_file_not_found(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        store.load_indexed_video(
            USER_ID,
            "missing",
        )

def test_save_and_load_empty_indexed_video(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    _save_video(
        store,
        tmp_path,
        transcripts=[],
        frames=[],
    )

    loaded = store.load_indexed_video(
        USER_ID,
        VIDEO_ID,
    )

    assert (
        loaded.indexed_video.transcript_segments
        == []
    )

    assert (
        loaded.indexed_video.video_frames
        == []
    )

def test_update_metadata(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    _save_video(
        store,
        tmp_path,
    )

    store.update_metadata(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        updates={
            "title": "Updated Lecture",
            "duration": 300,
        },
    )

    loaded = store.load_indexed_video(
        USER_ID,
        VIDEO_ID,
    )

    assert (
        loaded.metadata["title"]
        == "Updated Lecture"
    )

    assert (
        loaded.metadata["duration"]
        == 300
    )

    assert (
        loaded.metadata["filename"]
        == "lecture.mp4"
    )

def test_get_video_url_returns_video_path(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    _save_video(
        store,
        tmp_path,
    )

    url = store.get_video_url(
        USER_ID,
        VIDEO_ID,
    )

    expected_path = (
        tmp_path
        / "data"
        / USER_ID
        / VIDEO_ID
        / "lecture.mp4"
    )

    assert url == str(
        expected_path.absolute(),
    )

def test_save_thumbnail_creates_thumbnail(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    video_path = _create_video(
        tmp_path,
    )

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={},
    )

    thumbnail = np.zeros(
        (100, 100, 3),
        dtype=np.uint8,
    )

    store.save_thumbnail(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        thumbnail=thumbnail,
    )

    thumbnail_path = (
        tmp_path
        / "data"
        / USER_ID
        / VIDEO_ID
        / "thumbnail.jpg"
    )

    assert thumbnail_path.exists()

def test_get_thumbnail_url_returns_thumbnail_path(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    video_path = _create_video(
        tmp_path,
    )

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={},
    )

    thumbnail = np.zeros(
        (100, 100, 3),
        dtype=np.uint8,
    )

    store.save_thumbnail(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        thumbnail=thumbnail,
    )

    url = store.get_thumbnail_url(
        USER_ID,
        VIDEO_ID,
    )

    expected_path = (
        tmp_path
        / "data"
        / USER_ID
        / VIDEO_ID
        / "thumbnail.jpg"
    )

    assert url == str(
        expected_path.absolute(),
    )

def test_load_all_metadata_returns_all_videos(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    _save_video(
        store,
        tmp_path,
        video_id="video1",
        filename="lecture.mp4",
    )

    _save_video(
        store,
        tmp_path,
        video_id="video2",
        filename="cats.mp4",
    )

    metadata = store.load_all_metadata(
        USER_ID,
    )

    assert len(metadata) == 2

    filenames = {
        video["filename"]
        for video in metadata
    }

    assert filenames == {
        "lecture.mp4",
        "cats.mp4",
    }

def test_load_all_metadata_returns_empty_list_for_missing_user(
    tmp_path,
):
    store = _create_store(
        tmp_path,
    )

    metadata = store.load_all_metadata(
        USER_ID,
    )

    assert metadata == []