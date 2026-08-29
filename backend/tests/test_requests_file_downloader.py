from pathlib import Path
from unittest.mock import MagicMock, patch
from src.frame_finder.pipeline.classes.requests_file_downloader import RequestsFileDownloader
import pytest, requests

@pytest.fixture
def downloader():
    return RequestsFileDownloader()


@patch(
    "src.frame_finder.pipeline.classes.requests_file_downloader.requests.get"
)
def test_download_writes_response_to_file(
    mock_get,
    downloader,
    tmp_path: Path,
):
    response = MagicMock()

    response.iter_content.return_value = [
        b"hello ",
        b"world",
    ]

    mock_get.return_value.__enter__.return_value = response

    destination = tmp_path / "video.mp4"

    downloader.download(
        "https://example.com/video.mp4",
        destination,
    )

    assert destination.read_bytes() == b"hello world"

    mock_get.assert_called_once_with(
        "https://example.com/video.mp4",
        stream=True,
    )

    response.raise_for_status.assert_called_once()


@patch(
    "src.frame_finder.pipeline.classes.requests_file_downloader.requests.get"
)
def test_download_ignores_empty_chunks(
    mock_get,
    downloader,
    tmp_path: Path,
):
    response = MagicMock()

    response.iter_content.return_value = [
        b"hello",
        b"",
        b"world",
        b"",
    ]

    mock_get.return_value.__enter__.return_value = response

    destination = tmp_path / "video.mp4"

    downloader.download(
        "https://example.com/video.mp4",
        destination,
    )

    assert destination.read_bytes() == b"helloworld"


@patch(
    "src.frame_finder.pipeline.classes.requests_file_downloader.requests.get"
)
def test_download_raises_when_request_fails(
    mock_get,
    downloader,
    tmp_path: Path,
):
    response = MagicMock()

    error = requests.exceptions.HTTPError("404")

    response.raise_for_status.side_effect = error

    mock_get.return_value.__enter__.return_value = response

    destination = tmp_path / "video.mp4"

    with pytest.raises(requests.exceptions.HTTPError):
        downloader.download(
            "https://example.com/video.mp4",
            destination,
        )

    assert not destination.exists()