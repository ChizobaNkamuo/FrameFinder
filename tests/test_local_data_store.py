import torch, pytest
from pathlib import Path

from frame_finder.pipeline.classes.local_data_store import LocalDataStore
from frame_finder.data_classes.indexed_video import IndexedVideo
from frame_finder.data_classes.transcript_segment import TranscriptSegment


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


def _indexed_video() -> IndexedVideo:
    return IndexedVideo(
        transcript_segments=[
            _segment(0.0, 2.0, "Hello"),
            _segment(2.0, 4.0, "World"),
        ],
        video_frames=[],
    )


def _create_store(tmp_path: Path) -> LocalDataStore:
    store = LocalDataStore()
    store._root = tmp_path

    return store


def test_save_creates_expected_files(tmp_path):
    store = _create_store(tmp_path)
    video = _indexed_video()

    store.save(
        username="alice",
        video_id="video1",
        indexed_video=video,
    )

    directory = tmp_path / "alice" / "video1"

    assert directory.exists()

    assert (directory / "transcript_metadata.json").exists()
    assert (directory / "transcript_embeddings.pt").exists()


def test_load_returns_original_transcript_segments(tmp_path):
    store = _create_store(tmp_path)
    video = _indexed_video()

    store.save(
        username="alice",
        video_id="video1",
        indexed_video=video,
    )

    loaded = store.load(
        username="alice",
        video_id="video1",
    )

    assert len(loaded.transcript_segments) == 2

    expected = video.transcript_segments
    actual = loaded.transcript_segments

    for e, a in zip(expected, actual):

        assert e.start == a.start
        assert e.end == a.end
        assert e.text == a.text

        assert torch.equal(
            e.embedding,
            a.embedding,
        )


def test_load_returns_empty_video_frames(tmp_path):
    store = _create_store(tmp_path)
    video = _indexed_video()

    store.save(
        username="alice",
        video_id="video1",
        indexed_video=video,
    )

    loaded = store.load(
        username="alice",
        video_id="video1",
    )

    assert loaded.video_frames == []


def test_load_missing_video_raises_file_not_found(tmp_path):
    store = _create_store(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.load(
            username="alice",
            video_id="missing",
        )


def test_save_then_load_round_trip(tmp_path):
    store = _create_store(tmp_path)
    original = _indexed_video()

    store.save(
        username="alice",
        video_id="video1",
        indexed_video=original,
    )

    loaded = store.load(
        username="alice",
        video_id="video1",
    )

    assert len(original.transcript_segments) == len(
        loaded.transcript_segments
    )

    for o, l in zip(
        original.transcript_segments,
        loaded.transcript_segments,
    ):

        assert o.start == l.start
        assert o.end == l.end
        assert o.text == l.text

        assert torch.equal(
            o.embedding,
            l.embedding,
        )