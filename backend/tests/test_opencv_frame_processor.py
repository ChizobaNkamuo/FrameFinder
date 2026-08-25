from unittest.mock import MagicMock, patch
from src.frame_finder.pipeline.classes.open_cv_frame_processor import OpenCVFrameProcessor
import src.frame_finder.pipeline.classes.open_cv_frame_processor as fp
import torch
import pytest


def create_capture(fps=30):

    capture = MagicMock()

    capture.isOpened.return_value = True
    capture.get.return_value = fps

    return capture


def create_embedding_model():

    embedding_model = MagicMock()
    embedding_model.embed_image.return_value = torch.randn(512)

    return embedding_model


def create_frame():
    return object()


def test_constructor_stores_embedding_model():

    embedding_model = create_embedding_model()

    processor = OpenCVFrameProcessor(embedding_model)

    assert processor._embedding_model is embedding_model


def test_process_frames_invalid_video_raises():

    capture = MagicMock()
    capture.isOpened.return_value = False

    embedding_model = create_embedding_model()

    with patch.object(fp.cv2, "VideoCapture", return_value=capture):

        processor = OpenCVFrameProcessor(embedding_model)

        with pytest.raises(ValueError):
            processor.process_frames(
                "video.mp4",
                sample_rate=1.0,
            )


def test_process_frames_invalid_fps_raises():

    capture = create_capture(fps=0)

    embedding_model = create_embedding_model()

    with patch.object(fp.cv2, "VideoCapture", return_value=capture):

        processor = OpenCVFrameProcessor(embedding_model)

        with pytest.raises(ValueError):
            processor.process_frames(
                "video.mp4",
                sample_rate=1.0,
            )

    capture.release.assert_called_once()


def test_process_frames_samples_correct_frames():

    capture = create_capture(fps=2)

    frames = [
        (True, create_frame()),
        (True, create_frame()),
        (True, create_frame()),
        (True, create_frame()),
        (False, None),
    ]

    capture.read.side_effect = frames

    embedding_model = create_embedding_model()

    with (
        patch.object(fp.cv2, "VideoCapture", return_value=capture),
        patch.object(fp.cv2, "cvtColor", side_effect=lambda x, _: x),
    ):

        processor = OpenCVFrameProcessor(embedding_model)

        result = processor.process_frames(
            "video.mp4",
            sample_rate=1.0,
        )

        assert len(result) == 2

        assert result[0].timestamp == 0.0
        assert result[1].timestamp == 1.0

        assert embedding_model.embed_image.call_count == 2

    capture.release.assert_called_once()


def test_process_frames_returns_empty_list_when_video_has_no_frames():

    capture = create_capture()

    capture.read.return_value = (False, None)

    embedding_model = create_embedding_model()

    with patch.object(fp.cv2, "VideoCapture", return_value=capture):

        processor = OpenCVFrameProcessor(embedding_model)

        result = processor.process_frames(
            "video.mp4",
            sample_rate=1.0,
        )

        assert result == []

    capture.release.assert_called_once()


def test_process_frames_converts_frames_to_rgb_before_embedding():

    capture = create_capture()

    frame = create_frame()

    capture.read.side_effect = [
        (True, frame),
        (False, None),
    ]

    rgb_frame = object()

    embedding_model = create_embedding_model()

    with (
        patch.object(fp.cv2, "VideoCapture", return_value=capture),
        patch.object(fp.cv2, "cvtColor", return_value=rgb_frame) as mock_convert,
    ):

        processor = OpenCVFrameProcessor(embedding_model)

        processor.process_frames(
            "video.mp4",
            sample_rate=1.0,
        )

        mock_convert.assert_called_once_with(
            frame,
            fp.cv2.COLOR_BGR2RGB,
        )

        embedding_model.embed_image.assert_called_once_with(
            rgb_frame,
        )