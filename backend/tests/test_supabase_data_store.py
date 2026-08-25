from src.frame_finder.data.classes.supabase_data_store import SupabaseDataStore
from src.frame_finder.data_classes.transcript_segment import TranscriptSegment
from src.frame_finder.data_classes.video_frame import VideoFrame
from unittest.mock import MagicMock, patch
import pytest, torch, json
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


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def store(mock_client) -> SupabaseDataStore:
    return SupabaseDataStore(mock_client)

def _assert_transcripts_equal(
    expected: list[TranscriptSegment],
    actual: list[TranscriptSegment],
):
    assert len(expected) == len(actual)

    for expected_segment, actual_segment in zip(
        expected,
        actual,
    ):
        assert expected_segment.start == actual_segment.start
        assert expected_segment.end == actual_segment.end
        assert expected_segment.text == actual_segment.text

        assert torch.equal(
            expected_segment.embedding,
            actual_segment.embedding,
        )


def _assert_frames_equal(
    expected: list[VideoFrame],
    actual: list[VideoFrame],
):
    assert len(expected) == len(actual)

    for expected_frame, actual_frame in zip(
        expected,
        actual,
    ):
        assert expected_frame.timestamp == actual_frame.timestamp

        assert torch.equal(
            expected_frame.embedding,
            actual_frame.embedding,
        )

def test_save_upload_uploads_video_and_saves_metadata(
    store,
    mock_client,
    tmp_path,
):
    video_path = tmp_path / "lecture.mp4"
    video_path.write_bytes(b"fake video")

    store.save_upload(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_path=video_path,
        metadata={
            "status": "processing",
            "stage": "Uploading...",
        },
    )

    mock_client.storage.from_.assert_called_once_with(
        "videos"
    )

    storage_bucket = (
        mock_client.storage.from_.return_value
    )

    storage_bucket.upload.assert_called_once_with(
        path="alice/video1/lecture.mp4",
        file=video_path,
        file_options={
            "content-type": "video/mp4",
        },
    )

    mock_client.table.assert_called_with(
        "videos"
    )

    videos_table = mock_client.table.return_value

    videos_table.insert.assert_called_once_with(
        {
            "id": "video1",
            "user_id": "alice",
            "filename": "lecture.mp4",
            "status": "processing",
            "stage": "Uploading...",
        }
    )

    videos_table.insert.return_value.execute.assert_called_once()

def test_save_transcripts_inserts_expected_rows(
    store,
    mock_client,
):
    transcripts = _transcripts()

    store.save_transcripts(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        transcript_segments=transcripts,
    )

    expected_rows = []

    for segment in transcripts:
        expected_rows.append(
            {
                "video_id": VIDEO_ID,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
                "embedding": (
                    segment.embedding
                    .detach()
                    .cpu()
                    .tolist()
                ),
            }
        )

    mock_client.table.assert_called_with(
        "transcript_segments"
    )

    transcripts_table = (
        mock_client.table.return_value
    )

    transcripts_table.insert.assert_called_once()

    actual_rows = (
        transcripts_table.insert.call_args.args[0]
    )

    assert len(actual_rows) == len(expected_rows)

    for actual, expected in zip(
        actual_rows,
        expected_rows,
    ):
        assert actual["video_id"] == expected["video_id"]
        assert actual["start"] == expected["start"]
        assert actual["end"] == expected["end"]
        assert actual["text"] == expected["text"]

        assert torch.equal(
            torch.tensor(actual["embedding"]),
            torch.tensor(expected["embedding"]),
        )

    transcripts_table.insert.return_value.execute.assert_called_once()

def test_save_empty_transcripts_does_nothing(
    store,
    mock_client,
):
    store.save_transcripts(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        transcript_segments=[],
    )

    mock_client.table.assert_not_called()

def test_save_video_frames_inserts_expected_rows(
    store,
    mock_client,
):
    frames = _frames()

    store.save_video_frames(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_frames=frames,
    )

    mock_client.table.assert_called_with(
        "video_frames"
    )

    frames_table = (
        mock_client.table.return_value
    )

    frames_table.insert.assert_called_once()

    actual_rows = (
        frames_table.insert.call_args.args[0]
    )

    assert len(actual_rows) == len(frames)

    for actual, expected in zip(
        actual_rows,
        frames,
    ):
        assert actual["video_id"] == VIDEO_ID
        assert actual["timestamp"] == expected.timestamp

        assert torch.equal(
            torch.tensor(actual["embedding"]),
            expected.embedding,
        )

    frames_table.insert.return_value.execute.assert_called_once()

def test_save_empty_video_frames_does_nothing(
    store,
    mock_client,
):
    store.save_video_frames(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        video_frames=[],
    )

    mock_client.table.assert_not_called()

def test_load_indexed_video_returns_expected_data(
    store,
    mock_client,
):
    transcripts = _transcripts()
    frames = _frames()

    transcript_rows = [
        {
            "video_id": VIDEO_ID,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "embedding": json.dumps(
                segment.embedding.tolist()
            ),
        }
        for segment in transcripts
    ]

    frame_rows = [
        {
            "video_id": VIDEO_ID,
            "timestamp": frame.timestamp,
            "embedding": json.dumps(
                frame.embedding.tolist()
            ),
        }
        for frame in frames
    ]

    metadata = {
        "id": VIDEO_ID,
        "user_id": USER_ID,
        "filename": "lecture.mp4",
        "status": "complete",
    }

    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = metadata

    def table_side_effect(table_name):
        table = MagicMock()

        if table_name == "videos":
            (
                table
                .select.return_value
                .eq.return_value
                .eq.return_value
                .single.return_value
                .execute.return_value
                .data
            ) = metadata

        elif table_name == "transcript_segments":
            (
                table
                .select.return_value
                .eq.return_value
                .order.return_value
                .execute.return_value
                .data
            ) = transcript_rows

        elif table_name == "video_frames":
            (
                table
                .select.return_value
                .eq.return_value
                .order.return_value
                .execute.return_value
                .data
            ) = frame_rows

        return table

    mock_client.table.side_effect = table_side_effect

    loaded = store.load_indexed_video(
        USER_ID,
        VIDEO_ID,
    )

    assert loaded.metadata == metadata

    _assert_transcripts_equal(
        transcripts,
        loaded.indexed_video.transcript_segments,
    )

    _assert_frames_equal(
        frames,
        loaded.indexed_video.video_frames,
    )

def test_load_empty_indexed_video(
    store,
    mock_client,
):
    metadata = {
        "id": VIDEO_ID,
        "user_id": USER_ID,
        "filename": "lecture.mp4",
    }

    def table_side_effect(table_name):
        table = MagicMock()

        if table_name == "videos":
            (
                table
                .select.return_value
                .eq.return_value
                .eq.return_value
                .single.return_value
                .execute.return_value
                .data
            ) = metadata

        elif table_name == "transcript_segments":
            (
                table
                .select.return_value
                .eq.return_value
                .order.return_value
                .execute.return_value
                .data
            ) = []

        elif table_name == "video_frames":
            (
                table
                .select.return_value
                .eq.return_value
                .order.return_value
                .execute.return_value
                .data
            ) = []

        return table

    mock_client.table.side_effect = table_side_effect

    loaded = store.load_indexed_video(
        USER_ID,
        VIDEO_ID,
    )

    assert loaded.metadata == metadata

    assert (
        loaded.indexed_video.transcript_segments
        == []
    )

    assert (
        loaded.indexed_video.video_frames
        == []
    )

def test_update_metadata(
    store,
    mock_client,
):
    updates = {
        "status": "complete",
        "stage": "Finished",
    }

    store.update_metadata(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        updates=updates,
    )

    mock_client.table.assert_called_once_with(
        "videos"
    )

    table = mock_client.table.return_value

    table.update.assert_called_once_with(
        updates
    )

    table.update.return_value.eq.assert_called_once_with(
        "id",
        VIDEO_ID,
    )

    (
        table
        .update.return_value
        .eq.return_value
        .eq
        .assert_called_once_with(
            "user_id",
            USER_ID,
        )
    )

    (
        table
        .update.return_value
        .eq.return_value
        .eq.return_value
        .execute
        .assert_called_once()
    )

def test_load_all_metadata_returns_all_videos(
    store,
    mock_client,
):
    metadata = [
        {
            "id": "video1",
            "user_id": USER_ID,
            "filename": "lecture.mp4",
        },
        {
            "id": "video2",
            "user_id": USER_ID,
            "filename": "cats.mp4",
        },
    ]

    response = MagicMock()
    response.data = metadata

    (
        mock_client
        .table.return_value
        .select.return_value
        .eq.return_value
        .execute.return_value
    ) = response

    videos = store.load_all_metadata(
        USER_ID
    )

    assert videos == metadata

    mock_client.table.assert_called_once_with(
        "videos"
    )

    mock_client.table.return_value.select.assert_called_once_with(
        "*"
    )

    mock_client.table.return_value.select.return_value.eq.assert_called_once_with(
        "user_id",
        USER_ID,
    )

def test_load_all_metadata_returns_empty_list(
    store,
    mock_client,
):
    response = MagicMock()
    response.data = []

    (
        mock_client
        .table.return_value
        .select.return_value
        .eq.return_value
        .execute.return_value
    ) = response

    videos = store.load_all_metadata(
        USER_ID
    )

    assert videos == []

def test_get_video_url_returns_signed_url(
    store,
    mock_client,
):
    filename_response = MagicMock()
    filename_response.data = {
        "filename": "lecture.mp4",
    }

    (
        mock_client
        .table.return_value
        .select.return_value
        .eq.return_value
        .eq.return_value
        .single.return_value
        .execute.return_value
    ) = filename_response

    storage_bucket = (
        mock_client.storage.from_.return_value
    )

    storage_bucket.create_signed_url.return_value = {
        "signedURL": (
            "https://example.com/"
            "signed-video-url"
        )
    }

    result = store.get_video_url(
        USER_ID,
        VIDEO_ID,
    )

    assert result == (
        "https://example.com/"
        "signed-video-url"
    )

    mock_client.storage.from_.assert_called_once_with(
        "videos"
    )

    storage_bucket.create_signed_url.assert_called_once_with(
        path="alice/video1/lecture.mp4",
        expires_in=3600,
    )

def test_get_thumbnail_url_returns_signed_url(
    store,
    mock_client,
):
    storage_bucket = (
        mock_client.storage.from_.return_value
    )

    storage_bucket.create_signed_url.return_value = {
        "signedURL": (
            "https://example.com/"
            "signed-thumbnail-url"
        )
    }

    result = store.get_thumbnail_url(
        USER_ID,
        VIDEO_ID,
    )

    assert result == (
        "https://example.com/"
        "signed-thumbnail-url"
    )

    mock_client.storage.from_.assert_called_once_with(
        "videos"
    )

    storage_bucket.create_signed_url.assert_called_once_with(
        path="alice/video1/thumbnail.jpg",
        expires_in=3600,
    )

def test_save_thumbnail_uploads_encoded_image(
    store,
    mock_client,
):
    thumbnail = np.zeros(
        (100, 100, 3),
        dtype=np.uint8,
    )

    store.save_thumbnail(
        user_id=USER_ID,
        video_id=VIDEO_ID,
        thumbnail=thumbnail,
    )

    mock_client.storage.from_.assert_called_once_with(
        "videos"
    )

    storage_bucket = (
        mock_client.storage.from_.return_value
    )

    storage_bucket.upload.assert_called_once()

    call_kwargs = (
        storage_bucket.upload.call_args.kwargs
    )

    assert (
        call_kwargs["path"]
        == "alice/video1/thumbnail.jpg"
    )

    assert isinstance(
        call_kwargs["file"],
        bytes,
    )

    assert (
        call_kwargs["file_options"]
        == {
            "content-type": "image/jpeg",
            "upsert": "true",
        }
    )

def test_save_thumbnail_raises_when_encoding_fails(
    store,
    mock_client,
):
    thumbnail = np.zeros(
        (100, 100, 3),
        dtype=np.uint8,
    )

    with patch(
        "src.frame_finder.data.classes.supabase_data_store.cv2.imencode",
        return_value=(False, None),
    ):
        with pytest.raises(
            ValueError,
            match="Failed to encode thumbnail",
        ):
            store.save_thumbnail(
                user_id=USER_ID,
                video_id=VIDEO_ID,
                thumbnail=thumbnail,
            )

    mock_client.storage.from_.assert_not_called()

def test_to_tensor_from_json_string(
    store,
):
    embedding = [0.1, 0.2, 0.3]

    result = store._to_tensor(
        json.dumps(embedding)
    )

    expected = torch.tensor(
        embedding,
        dtype=torch.float32,
    )

    assert torch.equal(
        result,
        expected,
    )

